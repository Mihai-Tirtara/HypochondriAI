#!/bin/bash
set -e

echo "Getting ECR repository URL..."
cd terraform/environments/prod
if ! ECR_URL=$(terraform output -raw ecr_repository_url); then
    echo "ERROR: Failed to get ECR repository URL. Make sure ECR module is deployed:"
    exit 1
fi
REGION=$(echo $ECR_URL | cut -d'.' -f4)
echo "ECR Repository: $ECR_URL"

echo "Authenticating with ECR..."
if ! aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URL; then
    echo "ERROR: Failed to authenticate with ECR. Check AWS credentials and permissions."
    exit 1
fi

echo "Building Docker image..."
cd ../../../backend
if ! docker build -t hypochondriai-backend .; then
    echo "ERROR: Docker build failed. Check Dockerfile and dependencies."
    exit 1
fi

echo "Tagging image..."
 docker tag hypochondriai-backend:latest ${ECR_URL}:latest

echo "Pushing to ECR..."
if ! docker push ${ECR_URL}:latest; then
    echo "ERROR: Failed to push image to ECR. Check network connection and ECR permissions."
    exit 1
fi

echo "SUCCESS: Image pushed to ${ECR_URL}:latest"
