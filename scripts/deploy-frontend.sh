#!/bin/bash

# Frontend deployment script for S3 + CloudFront
set -e

# Configuration
PROJECT_NAME="hypochondriai"
ENVIRONMENT="prod"
AWS_REGION="eu-central-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    log_error "jq is required but not installed. Please install jq."
fi

# Get Terraform outputs
log_info "Getting Terraform outputs..."
cd terraform/environments/prod

if ! terraform output -json > /tmp/terraform_outputs.json; then
    log_error "Failed to get Terraform outputs. Make sure Terraform has been applied."
fi

S3_BUCKET=$(jq -r '.frontend_s3_bucket_name.value' /tmp/terraform_outputs.json)
CLOUDFRONT_DISTRIBUTION_ID=$(jq -r '.frontend_cloudfront_distribution_id.value' /tmp/terraform_outputs.json)
ALB_DNS_NAME=$(jq -r '.alb_dns_name.value' /tmp/terraform_outputs.json)

if [[ "$S3_BUCKET" == "null" ]] || [[ "$CLOUDFRONT_DISTRIBUTION_ID" == "null" ]]; then
    log_error "Required Terraform outputs not found. Please ensure S3-CloudFront module is deployed."
fi

log_info "S3 Bucket: $S3_BUCKET"
log_info "CloudFront Distribution ID: $CLOUDFRONT_DISTRIBUTION_ID"
log_info "Backend ALB: https://$ALB_DNS_NAME"

# Go back to project root
cd ../../..

# Build frontend with environment variables
log_info "Building frontend..."
cd frontend

# Set build-time environment variables
export VITE_API_BASE_URL="https://$ALB_DNS_NAME"
export VITE_SUPERUSER_NAME="${VITE_SUPERUSER_NAME:-admin}"

# Install dependencies if needed
if [[ ! -d "node_modules" ]]; then
    log_info "Installing dependencies..."
    npm install
fi

# Build the project
if ! npm run build; then
    log_error "Frontend build failed"
fi

log_success "Frontend built successfully"

# Upload to S3
log_info "Uploading files to S3..."

# Sync all files to S3 with appropriate cache headers
aws s3 sync dist/ "s3://$S3_BUCKET/" --delete --exact-timestamps

# Set specific cache headers for different file types
log_info "Setting cache headers..."

# HTML files - no cache
aws s3 cp "s3://$S3_BUCKET/" "s3://$S3_BUCKET/" \
    --recursive --exclude "*" --include "*.html" \
    --metadata-directive REPLACE \
    --cache-control "no-cache, no-store, must-revalidate" \
    --expires "0"

# Static assets - long cache
aws s3 cp "s3://$S3_BUCKET/" "s3://$S3_BUCKET/" \
    --recursive --exclude "*" --include "assets/*" \
    --metadata-directive REPLACE \
    --cache-control "public, max-age=31536000, immutable"

log_success "Files uploaded to S3"

# Create CloudFront invalidation
log_info "Creating CloudFront invalidation..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text)

log_info "CloudFront invalidation created: $INVALIDATION_ID"
log_info "Waiting for invalidation to complete (this may take several minutes)..."

# Wait for invalidation to complete
aws cloudfront wait invalidation-completed \
    --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
    --id "$INVALIDATION_ID"

log_success "CloudFront invalidation completed"

# Get the final URL
WEBSITE_URL=$(jq -r '.frontend_website_url.value' /tmp/terraform_outputs.json)
log_success "Frontend deployment complete!"
log_success "Website URL: $WEBSITE_URL"

# Cleanup
rm -f /tmp/terraform_outputs.json

cd ..
log_success "Deployment finished successfully!"
