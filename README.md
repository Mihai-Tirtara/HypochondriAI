# HyphochondriaAI

A comprehensive chatbot for providing AI-powered insights and support for people struggling with health anxiety.

## Project Architecture

The application consists of three main components:

1. **Backend API** - Python FastAPI service with LangChain integration
2. **Database** - PostgreSQL for conversation and user data persistence
3. **Frontend** - React application in Typescript 

## Local Development Setup

Follow these steps to set up and run the application locally:

### 1. Environment Setup

```bash
# Ensure you have Python 3.11+ and Node.js installed
# PostgreSQL database will be required according to config settings
```

### 2. Backend Service (Python FastAPI)

```bash
# Navigate to the backend directory
cd backend/app

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables in .env file
# Example:
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_aws_region
MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
DB_USERNAME=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=health_anxiety

# Start the FastAPI server
uvicorn main:app --reload
```

### 3. Frontend (React) 

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

## Current Project Status

- ✅ Migrated from Spring Boot to Python FastAPI backend
- ✅ Implemented LangChain conversation handling
- ✅ Added PostgreSQL database integration with SQLModel and Alembic
- ✅ Created comprehensive API endpoints for conversation management
- ✅ Testing framework and CI pipeline implemented
- ✅ Frontend compatible with new backend architecture
- ❌ Large UI improvements as the current is just a test version

## Next Steps

The  development roadmap in order of priority:

1. **Frontend Updates**:
   - Implement UI improvements for conversation flow
   - Add proper error handling
   - Add proper E2E testing

2. **Future Enhancements**:
   - Health Safety & Security Hardening
   - Cost Management & Monitoring
   - User authentication and session management
   - Docker containerization
   - Enhanced LLM Operations (Prompt optimization, RAG, etc)
   - Infrastructure & DevOps


## Troubleshooting

### Common Issues

1. **Backend Service Issues**
   * Verify database connection settings
   * Check AWS credentials for Bedrock access
   * Ensure all dependencies are installed

2. **Frontend API Connection** (when updated)
   * Verify backend is running on the expected port
   * Check for CORS issues in browser console

## License

This project is licensed under the MIT License - see the LICENSE file for details.
