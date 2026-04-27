from fastapi import FastAPI
from app.api import auth, user
from app.db.session import engine
from app.db.session import Base  # or wherever your Base is

Base.metadata.create_all(bind=engine)
from app.models.user import User  # must be imported
app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)

@app.get("/")
def root():
    return {"message": "Auth system running"}