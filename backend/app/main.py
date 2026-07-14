import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat
from app.routers import auth
from index_knowledge import build_knowledge_base

INDEX_FILE = Path("faiss_index/index.faiss")
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Verificando base de conocimiento (FAISS)...")
    
    if INDEX_FILE.exists():
        print("✅ Índice FAISS encontrado en el repo. Listo para usar.")
    else:
        print("⚠️ No se encontró faiss_index/. Esto no debería pasar en producción.")
        print("⚠️ Verifica que subiste la carpeta faiss_index/ a GitHub.")
        try:
            build_knowledge_base()
        except Exception as e:
            print(f"❌ No se pudo construir el índice automáticamente: {e}")
            print("❌ El servidor arrancará, pero el endpoint de chat probablemente fallará.")
            
    yield
    print("🛑 Cerrando servidor...")

app = FastAPI(
    title="TechAcademy RAG Agent API",
    description="API del agente inteligente para la escuela online TechAcademy",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")

app.include_router(chat.router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "online", "mensaje": "API RAG funcionando."}