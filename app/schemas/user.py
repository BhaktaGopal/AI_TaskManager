from pydantic import BaseModel, EmailStr


class UserListResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True  
        # Allows returning SQLAlchemy objects directly

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str