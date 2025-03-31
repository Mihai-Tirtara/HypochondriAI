# HypochondriAI

A supportive application designed to help users manage health anxiety through AI-assisted cognitive behavioral techniques and medical information contextualization.

## Project Overview

This application provides a platform for users to:
- Submit health symptoms and concerns
- Receive balanced, evidence-based responses
- Track conversation history
- Access personalized coping strategies

## Technical Architecture

The application consists of three main components:

1. **Frontend**: React + TypeScript with Tailwind CSS
2. **Backend API**: Spring Boot (Kotlin)
3. **LLM Service**: Python FastAPI with AWS Bedrock integration

## Prerequisites

Before setting up the application, ensure you have the following installed:

- Node.js (v16+) and npm
- Java Development Kit (JDK) 17+
- Kotlin
- Python 3.9+
- AWS account with Bedrock access

## Local Development Setup

Follow these steps to set up and run the application locally:

### 1. Environment Setup

```bash
# Ensure you have the necessary development environments ready
# No database configuration is required for the current version
```

### 2. LLM Service (Python FastAPI)

```bash
# Navigate to the LLM service directory
cd llm-service

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with AWS credentials
echo "AWS_ACCESS_KEY_ID=your_access_key" > .env
echo "AWS_SECRET_ACCESS_KEY=your_secret_key" >> .env
echo "AWS_REGION=your_aws_region" >> .env
echo "BEDROCK_MODEL_ID=your_model_id" >> .env

# Start the FastAPI server
uvicorn main:app --reload
```

**Note:** The LLM service must be running before starting the backend.

### 3. Backend API (Spring Boot)

```bash
# Navigate to the backend directory
cd backend

# Build the application
./gradlew build

# Run the application
./gradlew bootRun
```

### 4. Frontend (React)

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The application should now be running at `http://localhost:3000`

## Important Notes

- The LLM service must be started first, followed by the backend, and then the frontend
- Ensure all AWS Bedrock credentials are properly configured in the .env file
- The current version is a proof of concept and runs locally only
- Do not commit your .env file or AWS credentials to version control

## Troubleshooting

### Common Issues

1. **LLM Service Connection Issues**
   - Verify AWS credentials are correct
   - Ensure you have access to the specified AWS Bedrock model
   - Check network connectivity to AWS services

2. **Backend Service Issues**
   - Verify the Spring Boot application is running properly
   - Check logs for any initialization errors
   - Note: Database integration will be added in future versions

3. **Frontend API Connection**
   - Verify backend is running on the expected port
   - Check for CORS issues in browser console

## Next Steps After POC

Future enhancements planned for the application:
1. LangChain integration in the FastAPI service
2. Database integration with PostgreSQL
3. User authentication
4. UI Improved 
5. AWS API Gateway integration
6. Docker containerization
7. CI/CD pipeline setup
8. Additional features:
   - Personalized recommendations
   - Journal and symptom tracking
   - Professional resources directory

