from fastapi import FastAPI
from pydantic import BaseModel  

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
    return {
        "reply": f"You said: {request.message}"
    }