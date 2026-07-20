from sqlalchemy.orm import Session
from app.services.ai.rag_agent import answer_question
from app.services.db.chat_repository import save_message, get_recent_messages

def process_ai_question(db: Session, thread_id: int, question: str):
    # 1. Guardar pregunta del usuario usando el repositorio
    save_message(db, thread_id, sender="user", text=question)
    
    # 2. Obtener historial usando el repositorio
    message_history = get_recent_messages(db, thread_id)
    
    # 3. Obtener respuesta del agente
    try:
        response_text = answer_question(question, message_history)
    except Exception as e:
        print(f"Error calling Agent: {e}")
        response_text = "Lo siento, hubo un error técnico."
    
    # 4. Guardar respuesta IA usando el repositorio
    return save_message(db, thread_id, sender="ai", text=response_text)