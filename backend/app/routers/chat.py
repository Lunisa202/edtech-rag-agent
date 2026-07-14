from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatThread, Message, User
from app.routers.auth import get_current_user  # Reutilizamos tu lógica de auth
from typing import List
from app.schemas.chat import ThreadResponse, MessageResponse, MessageCreate
from app.services.rag_agent import answer_question


router = APIRouter(prefix="/chat", tags=["Chat"])

# Crear nuevo hilo
@router.post("/threads", response_model=ThreadResponse)
def create_thread(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_thread = ChatThread(user_id=current_user.id,
                            title="Nueva conversación")
    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)
    return new_thread

# Listar todos los hilos del usuario actual
@router.get("/threads", response_model=List[ThreadResponse])
def get_threads(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ChatThread).filter(ChatThread.user_id == current_user.id).order_by(ChatThread.created_at.desc()).all()

# Obtener todos los mensajes de un hilo específico (para cargar el historial)
@router.get("/threads/{thread_id}/messages", response_model=List[MessageResponse])
def get_messages(thread_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verificamos propiedad del hilo
    thread = db.query(ChatThread).filter(
        ChatThread.id == thread_id, ChatThread.user_id == current_user.id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Hilo no encontrado")

    return db.query(Message).filter(Message.thread_id == thread_id).order_by(Message.created_at.asc()).all()

# Obtener respuesta del agente con todo el contexto del hilo
@router.post("/threads/{thread_id}/ask", response_model=MessageResponse)
def ask_ai(thread_id: int, msg: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Verificar acceso al hilo
    thread = db.query(ChatThread).filter(
        ChatThread.id == thread_id, ChatThread.user_id == current_user.id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Hilo no encontrado")
    
    # Tomamos los primeros 40 caracteres de la pregunta del usuario como título
    if thread.title == "Nueva conversación":
        nuevo_titulo = msg.text[:40] 
        thread.title = nuevo_titulo
        db.commit()
    #  Guardar mensaje del usuario (es el primero en la secuencia)
   
    # Traemos los últimos 5 mensajes 
    message_history = db.query(Message)\
        .filter(Message.thread_id == thread_id)\
        .order_by(Message.created_at.desc())\
        .limit(10)\
        .all()
    message_history.reverse()  # Vuelve a ponerlos en orden cronológico

    user_message = Message(thread_id=thread_id, sender="user", text=msg.text)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    # Llamar al agente 
    try:
        response_text = answer_question(msg.text, message_history)
    except Exception as e:
        print(f"Error processing IA: {e}")
        response_text = "Lo siento, hubo un error técnico. Por favor, intenta de nuevo."

    # Guardar respuesta del agente en la base de datos
    ai_message = Message(thread_id=thread_id, sender="ai", text=response_text)
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)

    return ai_message

@router.delete("/threads/{thread_id}", status_code=204)
def delete_thread(
    thread_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Buscamos el hilo que pertenezca al usuario
    thread = db.query(ChatThread).filter(
        ChatThread.id == thread_id, 
        ChatThread.user_id == current_user.id
    ).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found or you don't have permission to delete it")

    # Borra los mensajes asociados 
    db.query(Message).filter(Message.thread_id == thread_id).delete()
    # 3. Borra el hilo
    db.delete(thread)
    db.commit()
    
    return None 