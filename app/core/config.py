from dotenv import load_dotenv
import os
load_dotenv()

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/ai_task_manager"
SECRET_KEY = "spsbhakta"   # later move to .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
print(f"Database URL: {DATABASE_URL}")