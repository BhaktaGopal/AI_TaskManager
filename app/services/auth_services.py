from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password,verify_password
from app.core.auth import create_access_token

def create_user(db: Session, email: str, password: str):
    hashed_password = hash_password(password)
    
    user = User(email=email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
def login_user(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)
    if not user:
        return None
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token}