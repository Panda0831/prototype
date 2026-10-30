from typing import Generator, List, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from src.db.session import SessionLocal
from src.db.models import User
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from src.utils.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/signin", auto_error=False)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme), 
    public_key: Optional[str] = Header(None), 
    db: Session = Depends(get_db)
):
    # 1. Tentative via JWT
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    return user
        except JWTError:
            pass

    # 2. Fallback via Header public-key (pour compatibilité immédiate)
    if public_key:
        user = db.query(User).filter(User.public_key == public_key).first()
        if user:
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Session invalide ou expirée. Veuillez vous reconnecter.",
        headers={"WWW-Authenticate": "Bearer"},
    )

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès non autorisé pour ce rôle"
            )
        return user
