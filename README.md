<div class="title-block" style="text-align: center;" align="center">

# HyphochondriaAI - Health Anxiety Specialist

<div align="center">
  <img src="images/logo2.png" alt="HyphochondriaAI Logo" width="300" height="300">
</div>

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/Mihai-Tirtara/HypochondriAI)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.6+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-GPL3.0-blue.svg)](LICENSE)
</div>


## Introduction
HyphochondriaAI is a chatbot designed to provide compassionate support and evidence-based information for individuals experiencing health anxiety. Built with modern web technologies and powered by advanced language models, it offers a safe space for users to explore their health concerns while promoting healthy coping mechanisms and encouraging appropriate medical consultation when necessary.


## Technology Stack & Features

- ⚡ **[FastAPI](https://fastapi.tiangolo.com)** for the Python backend API
  - 🧰 **[SQLModel](https://sqlmodel.tiangolo.com)** for database interactions (ORM)
  - 🔍 **[Pydantic](https://docs.pydantic.dev)** for data validation and settings management
  - ✅ **[Pytest](https://pytest.org)** for comprehensive testing
  - 🔄 **[Alembic](https://alembic.sqlalchemy.org/)** for database migrations
  - 💾 **[PostgreSQL](https://www.postgresql.org)** as the SQL database
  - 🔠 **[Ruff](https://github.com/astral-sh/ruff)** and **[Black](https://github.com/psf/black)** for linting and formatting

- 🚀 **[React](https://react.dev)** for the frontend
  - 💃 Using TypeScript, hooks, Vite, and other parts of a modern frontend stack.
  - 🎨 **[TailwindCSS](https://tailwindcss.com/)** for responsive design
  - 📱 An automatically generated frontend client
  - 🐕‍🦺 **[Husky](https://typicode.github.io/husky/)** with ESLint as Git hook

- 🤖 **[LangChain](https://langchain.com)** for LLM framework
  - 🌐 **[LangGraph](https://langgraph.com)** for agent creation and conversation memory
  - ☁️ **[AWS Bedrock](https://aws.amazon.com/bedrock/)** for AI model access
  - 🦾 **[Claude](https://claude.ai/new)** as the AI model
- 🏭 CI (continuous integration)  based on GitHub Actions.


### Main Page
[![API docs](images/main_page.png)](https://github.com/Mihai-Tirtara)

### Conversation Page
[![API docs](images/conversation_page.png)](https://github.com/Mihai-Tirtara)

### Interactive documentation
[![API docs](images/docs.png)](https://github.com/Mihai-Tirtara)


## Installation

Follow these steps to set up and run the application locally:

### 1. Environment Setup

```bash
# Ensure you have Python 3.12+ and Node.js installed
# PostgreSQL database will need to be created beforehand
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
fastapi dev
```

### 3. Frontend (React)

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run start
```

## License

This project is licensed under the GPL 3.0 License - see the LICENSE file for details.
