# AI Customer Support Chatbot

Production-style AI Customer Support Chatbot with FastAPI, Groq LLM, FAISS semantic search, PostgreSQL conversation memory, WhatsApp integration, Dockerized deployment, and streaming responses.

## Features

- REST API with FastAPI
- Pydantic request validation
- Groq LLM integration
- Secure API key management with `.env`
- Company policy knowledge base (RAG foundation)

## Project Status

🚧 Work in Progress

Next milestones:
- Document chunking
- Embeddings
- FAISS vector search
- Full RAG pipeline
- WhatsApp integration

## Architecture

User
   ↓
FastAPI API
   ↓
Groq LLM
   ↓
Company Knowledge Base
   ↓
Response

## Quick Start

```bash
git clone https://github.com/Farhaan2510/ai-customer-support-chatbot.git

cd ai-customer-support-chatbot

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

python -m uvicorn app.main:app --reload
```

## Demo

Open:

http://127.0.0.1:8000/docs

Use the `/chat` endpoint to interact with the chatbot.

