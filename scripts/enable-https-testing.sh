#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 Setting up self-signed HTTPS certificate for ALB testing...${NC}"

# Check if we're in the correct directory
if [ ! -d "terraform/environments/prod" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    echo -e "${YELLOW}Expected directory structure: terraform/environments/prod/${NC}"
    exit 1
fi

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Error: Terraform is not installed or not in PATH${NC}"
    exit 1
fi

# Check if aws cli is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ Error: AWS CLI is not installed or not in PATH${NC}"
    exit 1
fi

# Check if openssl is installed
if ! command -v openssl &> /dev/null; then
    echo -e "${RED}❌ Error: OpenSSL is not installed or not in PATH${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Getting infrastructure details from Terraform...${NC}"

# Get infrastructure details from Terraform
cd terraform/environments/prod

# Check if terraform state exists
if ! terraform show &> /dev/null; then
    echo -e "${RED}❌ Error: No Terraform state found. Please run 'terraform apply' first.${NC}"
    exit 1
fi

ALB_DNS=$(terraform output -raw alb_dns_name 2>/dev/null || echo "")
ALB_ARN=$(terraform output -raw alb_arn 2>/dev/null || echo "")
TARGET_GROUP_ARN=$(terraform output -raw target_group_arn 2>/dev/null || echo "")

# Validate outputs
if [ -z "$ALB_DNS" ] || [ -z "$ALB_ARN" ] || [ -z "$TARGET_GROUP_ARN" ]; then
    echo -e "${RED}❌ Error: Could not retrieve required Terraform outputs${NC}"
    echo "Expected outputs: alb_dns_name, alb_arn, target_group_arn"
    echo "Available outputs:"
    terraform output 2>/dev/null || echo "No outputs available"
    exit 1
fi

echo -e "${GREEN}✅ Retrieved infrastructure details:${NC}"
echo -e "  ALB DNS: ${YELLOW}$ALB_DNS${NC}"
echo -e "  ALB ARN: ${ALB_ARN}"
echo -e "  Target Group ARN: ${TARGET_GROUP_ARN}"

# Return to project root
cd ../../../

echo -e "${BLUE}🔑 Generating self-signed certificate...${NC}"

# Create temporary directory for certificate files
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Generate self-signed certificate
openssl req -x509 -newkey rsa:2048 -keyout private.key -out certificate.crt -days 365 -nodes \
    -subj "/C=US/ST=Test/L=Test/O=HypochondriAI/OU=Testing/CN=$ALB_DNS" \
    -addext "subjectAltName=DNS:$ALB_DNS" 2>/dev/null

echo -e "${GREEN}✅ Certificate generated successfully${NC}"

echo -e "${BLUE}☁️  Importing certificate to AWS Certificate Manager...${NC}"

# Import to ACM
CERT_ARN=$(aws acm import-certificate \
    --certificate fileb://certificate.crt \
    --private-key fileb://private.key \
    --query 'CertificateArn' --output text)

if [ -z "$CERT_ARN" ]; then
    echo -e "${RED}❌ Error: Failed to import certificate to ACM${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Certificate imported to ACM${NC}"
echo -e "  Certificate ARN: ${YELLOW}$CERT_ARN${NC}"

echo -e "${BLUE}🔗 Checking for existing HTTPS listener...${NC}"

# Check if HTTPS listener already exists
EXISTING_LISTENER=$(aws elbv2 describe-listeners \
    --load-balancer-arn "$ALB_ARN" \
    --query 'Listeners[?Port==`443`].ListenerArn' \
    --output text)

if [ -n "$EXISTING_LISTENER" ] && [ "$EXISTING_LISTENER" != "None" ]; then
    echo -e "${YELLOW}⚠️  HTTPS listener already exists. Updating certificate...${NC}"

    # Update existing listener with new certificate
    aws elbv2 modify-listener \
        --listener-arn "$EXISTING_LISTENER" \
        --certificates CertificateArn="$CERT_ARN" > /dev/null

    echo -e "${GREEN}✅ HTTPS listener certificate updated${NC}"
else
    echo -e "${BLUE}➕ Creating new HTTPS listener...${NC}"

    # Create new HTTPS listener
    LISTENER_ARN=$(aws elbv2 create-listener \
        --load-balancer-arn "$ALB_ARN" \
        --protocol HTTPS \
        --port 443 \
        --ssl-policy ELBSecurityPolicy-TLS-1-2-2017-01 \
        --certificates CertificateArn="$CERT_ARN" \
        --default-actions Type=forward,TargetGroupArn="$TARGET_GROUP_ARN" \
        --query 'Listeners[0].ListenerArn' --output text)

    if [ -z "$LISTENER_ARN" ]; then
        echo -e "${RED}❌ Error: Failed to create HTTPS listener${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ HTTPS listener created${NC}"
    echo -e "  Listener ARN: ${LISTENER_ARN}"
fi

# Cleanup temporary files
cd /
rm -rf "$TEMP_DIR"

echo -e "${GREEN}🎉 HTTPS setup complete!${NC}"
echo
echo -e "${BLUE}📝 Summary:${NC}"
echo -e "  🌐 ALB HTTPS URL: ${GREEN}https://$ALB_DNS${NC}"
echo -e "  📋 Certificate ARN: ${YELLOW}$CERT_ARN${NC}"
echo
echo -e "${YELLOW}🧪 Testing:${NC}"
echo -e "  curl -k https://$ALB_DNS/docs"
echo -e "  ${BLUE}(Use -k flag to ignore self-signed certificate warnings)${NC}"
echo
echo -e "${YELLOW}🗑️  To remove HTTPS setup:${NC}"
echo -e "  aws acm delete-certificate --certificate-arn $CERT_ARN"
echo -e "  aws elbv2 delete-listener --listener-arn <https-listener-arn>"
