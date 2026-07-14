
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials 
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User  # IMPORTANTE: Cambiado de Usuario a User
from app.core.security import get_password_hash, verify_password, create_access_token, verify_token, oauth2_scheme
from app.schemas.auth import UserCreate, Token, UserResponse

# Cambiamos el tag a inglés para consistencia
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Verificar si el correo ya existe
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email already registered"
        )
    
    # 2. Crear el nuevo usuario incluyendo el nombre
    new_user = User(
        email=user.email,
        password_hash=get_password_hash(user.password),
        auth_provider="local",
        full_name=user.full_name  # Guardamos el nombre aquí
        # profile_picture se queda en NULL automáticamente
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 3. Generar el JWT
    access_token = create_access_token(data={"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login_user(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Buscar al usuario
    db_user = db.query(User).filter(User.email == user.email).first()
    
    # 2. Verificar existencia y contraseña
    if not db_user or not db_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
        
    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
        
    # 3. Generar el JWT
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Aquí extraemos el string del token:
    token = credentials.credentials 
    
    # Ahora sí, pasamos el string a la función:
    payload = verify_token(token) 
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    return user