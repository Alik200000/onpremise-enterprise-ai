"""
Главное приложение FastAPI:
- On-Premise API для RAG и мультиагентного оркестратора
- Эндпоинты для загрузки документов (PDF, DXF, TXT)
- Статический Web UI (Open WebUI-style интерфейс)
"""

import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.parser import DocumentParser
from app.rag import rag_store
from app.agents import workflow

app = FastAPI(
    title="ТОО Enterprise AI (On-Premise)",
    description="Закрытый корпоративный ИИ с локальным RAG и мультиагентной системой безопасности",
    version="1.0.0"
)

# Включаем CORS для всех источников (поддержка браузерных запросов с GitHub Pages и внешних клиентов)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Монтируем статику
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Инициализируем базу знаний базовыми сэмплами при старте
@app.on_event("startup")
def load_initial_samples():
    samples_dir = os.path.join(os.path.dirname(__file__), "..", "data", "samples")
    if os.path.exists(samples_dir):
        for fname in os.listdir(samples_dir):
            fpath = os.path.join(samples_dir, fname)
            lower = fname.lower()
            if lower.endswith(".txt"):
                chunks = DocumentParser.parse_text(fpath, doc_type="GOST_OR_DOC")
                rag_store.add_chunks(chunks)
            elif lower.endswith((".dxf", ".dwg")):
                chunks = DocumentParser.parse_dxf(fpath)
                rag_store.add_chunks(chunks)
            elif lower.endswith(".pdf"):
                chunks = DocumentParser.parse_pdf(fpath)
                rag_store.add_chunks(chunks)
    try:
        print(f"[OK] Knowledge Base initialized: {len(rag_store.chunks)} chunks loaded.")
    except Exception:
        pass

class ChatQueryRequest(BaseModel):
    query: str
    user_role: str = "engineer"

@app.post("/api/chat")
async def process_chat(req: ChatQueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Запрос не может быть пустым")
    result = workflow.run(query=req.query, user_role=req.user_role)
    return JSONResponse(content=result)

@app.get("/api/knowledge-base")
async def get_knowledge_base():
    return {
        "total_chunks": len(rag_store.chunks),
        "documents": list(set([c.doc_name for c in rag_store.chunks]))
    }

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = file.filename
    save_dir = os.path.join(os.path.dirname(__file__), "..", "data", "uploads")
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunks = []
    lower_name = filename.lower()
    if lower_name.endswith(".pdf"):
        chunks = DocumentParser.parse_pdf(file_path)
    elif lower_name.endswith((".dxf", ".dwg")):
        chunks = DocumentParser.parse_dxf(file_path)
    else:
        chunks = DocumentParser.parse_text(file_path)

    rag_store.add_chunks(chunks)
    return {
        "success": True,
        "filename": filename,
        "chunks_indexed": len(chunks),
        "total_database_chunks": len(rag_store.chunks)
    }

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>UI загружается...</h1>")
