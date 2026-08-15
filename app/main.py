from fastapi import FastAPI
from pydantic import BaseModel  
from dotenv import load_dotenv
from openai import OpenAI

import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()
name = "Farhaan"

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def home():
    return {"message": "AI Customer Support Chatbot is running!"}

@app.get("/greet/{name}")
def greet(name):
    return {"message": f"Hello {name}!"}

@app.post("/chat")
def chat(request: ChatRequest):
    try:

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": request.message
                }
            ]
        )

        return {
            "reply": response.choices[0].message.content
        }
    
    except Exception as e:
        return{
            "error": str(e)
        }