from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from src.api.deps import get_db
from src.db.models import User
from src.api.schemas.auth import UserSignUp, UserSignIn, Token
from src.models.actors import Acteur, RoleActeur
from src.utils.crypto import Crypto
from src.utils.security import create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

router = APIRouter()

@router.post("/signup", response_model=Token)
async def signup(user_in: UserSignUp, db: Session = Depends(get_db)):
    print(f" [DEBUG] Tentative d'inscription: {user_in}")
    # Vérifier si l'utilisateur existe déjà
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    user_by_name = db.query(User).filter(User.username == user_in.username).first()
    if user_by_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris"
        )

    # Création d'un acteur pour générer les clés blockchain
    try:
        role_enum = RoleActeur[user_in.role.upper()]
    except KeyError:
        role_enum = RoleActeur.CITOYEN

    acteur = Acteur(nom=user_in.username, role=role_enum, district=user_in.district)
    
    # Création de l'utilisateur en base de données
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=Crypto.hacher_mot_de_passe(user_in.password),
        role=role_enum.value,
        district=user_in.district,
        public_key=str(acteur.cle_publique) # On stocke la clé publique
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": new_user.username,
        "public_key": new_user.public_key,
        "role": new_user.role
    }

@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"username": u.username, "public_key": u.public_key, "role": u.role} for u in users]

@router.post("/signin", response_model=Token)
async def signin(user_in: UserSignIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not Crypto.verifier_mot_de_passe(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "public_key": user.public_key,
        "role": user.role
    }
