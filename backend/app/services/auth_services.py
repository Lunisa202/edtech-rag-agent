from fastapi import HTTPException, status
from app.services.db.user_repository import get_user_by_email, create_user
from app.core.security import get_password_hash, verify_password, create_access_token

def authenticate_user(db, email, password):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return create_access_token(data={"sub": str(user.id)})

def register_new_user(db, user_data):
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Preparamos los datos
    data = {
        "email": user_data.email,
        "password_hash": get_password_hash(user_data.password),
        "auth_provider": "local",
        "full_name": user_data.full_name
    }
    return create_user(db, data)

from fastapi import HTTPException, status
from app.core.security import verify_token
from app.services.db.user_repository import get_user_by_id

def get_current_user_from_token(db, credentials):
    token = credentials.credentials 
    payload = verify_token(token) 
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    return user