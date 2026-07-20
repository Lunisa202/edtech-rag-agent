from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials 
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import verify_token, oauth2_scheme, create_access_token
from app.schemas.auth import UserCreate, Token, UserResponse
from app.services.auth_services import get_current_user_from_token
from app.services.auth_services import register_new_user, authenticate_user
from app.services.db.user_repository import get_user_by_id

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = register_new_user(db, user)
    access_token = create_access_token(data={"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login_user(user: UserCreate, db: Session = Depends(get_db)):
    access_token = authenticate_user(db, user.email, user.password)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    token = credentials.credentials 
    payload = verify_token(token) 
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    # Usamos el repositorio en lugar de hacer el db.query directo aquí
    user = get_user_by_id(db, int(user_id))
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    return user

@router.get("/me", response_model=UserResponse)
def get_current_user_route(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
):
    return get_current_user_from_token(db, credentials)