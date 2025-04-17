# HyphochondriaAI

A comprehensive application for providing AI-powered insights and support for health anxiety concerns.

## 🚨 Important Notice - Work in Progress 🚨

**The application is currently undergoing a major architectural change.**

- The frontend is temporarily not functioning due to backend API changes
- We're transitioning from Spring Boot to a Python FastAPI backend with LangChain implementation
- Follow the development setup instructions below to work with the current state

## Project Architecture

The application consists of three main components:

1. **Backend API** - Python FastAPI service with LangChain integration
2. **Database** - PostgreSQL for conversation and user data persistence
3. **Frontend** - React application (temporarily incompatible with current backend)

## Local Development Setup

Follow these steps to set up and run the application locally:

### 1. Environment Setup

```bash
# Ensure you have Python 3.9+ and Node.js installed
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

### 3. Frontend (React) - Currently Not Compatible

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
- ❌ Frontend not currently compatible with new backend architecture
- ❌ Testing framework not yet implemented

## Next Steps

Our development roadmap in order of priority:

1. **Backend Enhancements**:
   - Implement proper testing framework
   - Add code formatting and linting
   - Complete database migration scripts

2. **Frontend Updates**:
   - Update frontend to work with new API endpoints
   - Implement UI improvements for conversation flow
   - Add proper error handling

3. **Future Enhancements**:
   - User authentication and session management
   - Docker containerization
   - CI/CD pipeline setup
   - AWS API Gateway integration
   - Additional features:
     * Personalized recommendations
     * Journal and symptom tracking
     * Professional resources directory

## Troubleshooting

### Common Issues

1. **Backend Service Issues**
   * Verify database connection settings
   * Check AWS credentials for Bedrock access
   * Ensure all dependencies are installed

2. **Frontend API Connection** (when updated)
   * Verify backend is running on the expected port
   * Check for CORS issues in browser console

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
