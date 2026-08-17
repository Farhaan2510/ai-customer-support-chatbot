from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

from app.rag import (
    load_documents,
    split_into_chunks,
    create_embeddings,
    build_index,
    search,
)

import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

app = FastAPI()


# -------------------------
# Startup (Load Once)
# -------------------------

documents = load_documents()
chunks = split_into_chunks(documents)
embeddings = create_embeddings(chunks)
index = build_index(embeddings)


# -------------------------
# Conversation Memory
# -------------------------

class ConversationManager:

    def __init__(self):
        self.conversations = {}

    def add_message(self, session_id, role, content):

        if session_id not in self.conversations:
            self.conversations[session_id] = []

        self.conversations[session_id].append(
            {
                "role": role,
                "content": content
            }
        )

    def get_messages(self, session_id):
        return self.conversations.get(session_id, [])


conversation_manager = ConversationManager()


# -------------------------
# Request Model
# -------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str


# -------------------------
# Routes
# -------------------------

@app.get("/")
def home():
    return {"message": "AI Customer Support Chatbot is running!"}


@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello {name}!"}


@app.post("/chat")
def chat(request: ChatRequest):

    # Retrieve relevant company policy
    context = search(request.message, index, chunks)

    # Previous conversation
    previous_messages = conversation_manager.get_messages(
        request.session_id
    )

    messages = [
        {
            "role": "system",
            "content": f"""
You are a customer support assistant.

Use ONLY the provided company information.

If the answer is not present in the provided context, clearly say that the information is not available.
Do not invent company policies.

Relevant Company Information:

{context}
"""
        },
        *previous_messages,
        {
            "role": "user",
            "content": request.message
        }
    ]

    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        assistant_reply = response.choices[0].message.content

        # Save conversation AFTER generating the reply
        conversation_manager.add_message(
            request.session_id,
            "user",
            request.message
        )

        conversation_manager.add_message(
            request.session_id,
            "assistant",
            assistant_reply
        )

        return {
            "reply": assistant_reply
        }

    except Exception as e:
        return {
            "error": str(e)
        }