from sqlalchemy.orm import Session
from app.models import Message, ChatThread

def create_thread_db(db: Session, user_id: int) -> ChatThread:
    new_thread = ChatThread(user_id=user_id, title="Nueva conversación")
    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)
    return new_thread

def get_user_threads(db: Session, user_id: int) -> list:
    return db.query(ChatThread).filter(ChatThread.user_id == user_id).order_by(ChatThread.created_at.desc()).all()

def get_thread_by_id(db: Session, thread_id: int, user_id: int):
    return db.query(ChatThread).filter(
        ChatThread.id == thread_id, 
        ChatThread.user_id == user_id
    ).first()

def get_messages_by_thread(db: Session, thread_id: int) -> list:
    return db.query(Message).filter(Message.thread_id == thread_id).order_by(Message.created_at.asc()).all()

def save_message(db: Session, thread_id: int, sender: str, text: str) -> Message:
    new_message = Message(thread_id=thread_id, sender=sender, text=text)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_recent_messages(db: Session, thread_id: int, limit: int = 10) -> list:
    return db.query(Message)\
        .filter(Message.thread_id == thread_id)\
        .order_by(Message.created_at.desc())\
        .limit(limit)\
        .all()[::-1]

def delete_thread_db(db: Session, thread: ChatThread) -> None:
    # Borramos primero los mensajes asociados por seguridad de FK
    db.query(Message).filter(Message.thread_id == thread.id).delete()
    db.delete(thread)
    db.commit()