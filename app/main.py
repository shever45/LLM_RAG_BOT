from fastapi import FastAPI
from pydantic import BaseModel
from app.rag import load_docs,search

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
class ChatResponse(BaseModel):
    response: str
    session_id: str | None = None

app = FastAPI()

documents_main = load_docs()
print(f"загружено документов: {len(documents_main)}")

@app.get('/documents')
def list_docs():
    return {'files': list(documents_main.keys())}

@app.get('/')
def reader():
    return {'status':'ok', 'message':'работает'}

@app.post('/chat')
def chat(request: ChatRequest):
    context = search(request.message, documents_main)

    return ChatResponse(
        response = f'Подходящий файл {context}',
        session_id = request.session_id
    )