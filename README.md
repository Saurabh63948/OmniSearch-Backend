# OmniSearch-Backend

A Multi-Agent System (MAS) built with FastAPI and LangGraph for automated research and report generation.

## Overview
This backend system uses specialized AI agents to perform deep web research, scrape relevant data, and synthesize comprehensive reports. It includes a complete authentication system and persistent storage for chat sessions.

## Core Features
- JWT-based Authentication (Signup/Login)
- Research Pipeline using LangGraph agents
- Web Search integration via Tavily API
- Persistent storage in PostgreSQL (Supabase)
- Session-based chat history tracking

## Tech Stack
- Framework: FastAPI
- Database: PostgreSQL / SQLAlchemy
- AI: LangChain, LangGraph, HuggingFace
- Security: PyJWT, Passlib (bcrypt)

## Installation

1. Install dependencies:
   pip install -r requirements.txt

2. Configure Environment Variables (.env):
   DATABASE_URL=your_postgres_url
   SECRET_KEY=your_jwt_secret
   ALGORITHM=HS256
   TAVILY_API_KEY=your_api_key

3. Start the server:
   uvicorn main:app --reload

## Deployment on Render
- Build Command: pip install --no-cache-dir -r requirements.txt
- Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
- Note: Clear build cache if you encounter disk space issues.

## API Documentation
Once running, visit /docs for the interactive Swagger UI.
