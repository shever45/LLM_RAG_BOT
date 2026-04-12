from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid

from app.rag import load_docs,search
from app.agent import chat_with_agent

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
class ChatResponse(BaseModel):
    response: str
    session_id: str
    needs_clarification: bool = False

sessions: Dict[str, List[Dict[str,str]]] = {}

app = FastAPI(
    title="RAG Agent",
    description="Чат-бот для консультаций по международной стажировке CdekStart")

# documents_main = load_docs()
# print(f"загружено документов: {len(documents_main)}")

@app.get('/')
def read_root():
    return {
        "service": "CdekStart RAG Agent",
        "status": "running",
        "endpoints": {
            "chat": "/chat",
            "docs": "/docs"
        }
    }

@app.post('/chat', response_model=ChatResponse)
def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    history = sessions.get(session_id, [])

    result = chat_with_agent(request.message, history)

    sessions[session_id] = result['history']

    return ChatResponse(
        response = result['response'],
        session_id = session_id,
        needs_clarification = result['needs_clarification']
    )