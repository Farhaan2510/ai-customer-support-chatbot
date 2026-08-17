import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel
from sqlalchemy import text

from app.database import Base, SessionLocal, engine
from app.models import Message
from app.rag import (
    build_index,
    create_embeddings,
    load_documents,
    search,
    split_into_chunks,
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

app = FastAPI()

documents = load_documents()
chunks = split_into_chunks(documents)
embeddings = create_embeddings(chunks)
index = build_index(embeddings)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/")
def home():
    return {"message": "AI Customer Support Chatbot is running!"}


@app.get("/health")
def health():

    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
            "rag": "loaded"
        }

    finally:
        db.close()


@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello {name}!"}


@app.post("/chat")
def chat(request: ChatRequest):

    db = SessionLocal()

    try:

        context = search(request.message, index, chunks)

        history = (
            db.query(Message)
              .filter(Message.session_id == request.session_id)
              .order_by(Message.created_at)
              .all()
        )

        previous_messages = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in history
        ]

        messages = [
            {
                "role": "system",
                "content": f"""
You are a customer support assistant.

Answer ONLY using the company information below.

If the answer is not available,
say you don't have enough information.

Company Information:

{context}
"""
            },
            *previous_messages,
            {
                "role": "user",
                "content": request.message
            }
        ]

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            stream=True
        )

        def generate_response():

            assistant_reply = ""

            for chunk in response:

                text_chunk = chunk.choices[0].delta.content

                if text_chunk:

                    assistant_reply += text_chunk

                    yield text_chunk

            db.add(
                Message(
                    session_id=request.session_id,
                    role="user",
                    content=request.message
                )
            )

            db.add(
                Message(
                    session_id=request.session_id,
                    role="assistant",
                    content=assistant_reply
                )
            )

            db.commit()

        return StreamingResponse(
            generate_response(),
            media_type="text/plain"
        )

    except Exception as e:
        return {"error": str(e)}

    finally:
        db.close()