from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User
from app.routers.auth import get_current_user
from app.schemas.chat import ThreadResponse, MessageResponse, MessageCreate

# Importamos desde tus nuevas capas de servicio y repositorio
from app.services.ai.chat_services import process_ai_question
from app.services.db.chat_repository import (
    create_thread_db, 
    get_user_threads, 
    get_thread_by_id, 
    get_messages_by_thread, 
    delete_thread_db
)

router = APIRouter(prefix="/chat", tags=["Chat"])

# Crear nuevo hilo
@router.post("/threads", response_model=ThreadResponse)
def create_thread(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_thread_db(db, current_user.id)

# Listar todos los hilos del usuario actual
@router.get("/threads", response_model=List[ThreadResponse])
def get_threads(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_user_threads(db, current_user.id)

# Obtener todos los mensajes de un hilo específico
@router.get("/threads/{thread_id}/messages", response_model=List[MessageResponse])
def get_messages(thread_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    thread = get_thread_by_id(db, thread_id, current_user.id)
    if not thread:
        raise HTTPException(status_code=404, detail="Hilo no encontrado")
    
    return get_messages_by_thread(db, thread_id)

# Obtener respuesta del agente
@router.post("/threads/{thread_id}/ask", response_model=MessageResponse)
def ask_ai(thread_id: int, msg: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    thread = get_thread_by_id(db, thread_id, current_user.id)
    if not thread:
        raise HTTPException(status_code=404, detail="Hilo no encontrado")
    
    # Delegamos toda la lógica de IA y persistencia al servicio
    return process_ai_question(db, thread_id, msg.text)

# Eliminar hilo
@router.delete("/threads/{thread_id}", status_code=204)
def delete_thread(thread_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    thread = get_thread_by_id(db, thread_id, current_user.id)
    if not thread:
        raise HTTPException(status_code=404, detail="Hilo no encontrado")
    
    delete_thread_db(db, thread)
    return None