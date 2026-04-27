from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.services.auth_services import create_user, login_user
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User
from app.core.security import hash_password
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_services import authenticate_user, create_access_token
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    new_user = create_user(db,user.email, user.password)
 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 1. Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # 2. Create token
    access_token = create_access_token(data={"sub": user.email})

    # 3. Return response (OAuth2 compliant)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }