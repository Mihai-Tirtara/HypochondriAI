# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## HypochondriaAI

Health anxiety support chatbot with FastAPI backend, React frontend, and PostgreSQL database.

**Tech Stack**: FastAPI, LangChain/LangGraph, AWS Bedrock (Claude 3.5 Sonnet), SQLModel, React + TypeScript, Vite, Tailwind CSS

## Setup & Development

### Backend
* **Install dependencies**: `cd backend && pip install -r app/requirements.txt`
* **Run dev server**: `cd backend/app && uvicorn main:app --reload`
* **Apply migrations**: `cd backend/app && alembic upgrade head`
* **Create migration**: `cd backend/app && alembic revision --autogenerate -m "description"`

### Frontend
* **Install dependencies**: `cd frontend && npm install`
* **Run dev server**: `cd frontend && npm start`
* **Generate API client**: `cd frontend && npm run generate-client`
* **Build**: `cd frontend && npm run build`

## Testing & Code Quality

### Backend
* **Run tests**: `cd backend && pytest app/tests/`
* **Run single test**: `cd backend && pytest app/tests/path_to_test.py::test_name -v`
* **Lint**: `cd backend && ruff check app/`
* **Format**: `cd backend && black app/`

### Frontend
* **Lint**: `cd frontend && npm run lint`
* **Build check**: `cd frontend && npm run build`

## Code Style

### Backend (Python)
* **Naming**: snake_case for functions/variables, PascalCase for classes
* **Types**: Use SQLModel for database operations, type annotations required

### Frontend (TypeScript)
* **Components**: Function components with React hooks
* **Types**: Strict TypeScript mode with proper interfaces
* **Styling**: Tailwind CSS utility classes
* **API**: Use auto-generated client from OpenAPI spec

## Claude Code Guidelines

1. **Always run tests** after backend changes: `cd backend && pytest app/tests/`
2. **Regenerate API client** after backend API changes: `cd frontend && npm run generate-client` 
2. **Venv** When running Python or pip commands, ensure you are working inside the venv either by activating or by using the path to the relevant Python binary