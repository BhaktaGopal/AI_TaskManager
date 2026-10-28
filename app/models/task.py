from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class Task(Base):
    __tablename__ = "tasks"  
    # Table name in PostgreSQL

    id = Column(Integer, primary_key=True, index=True)  
    # Unique identifier for each task

    title = Column(String, nullable=False)  
    # Short title of the task (required)

    description = Column(String, nullable=True)  
    # Optional detailed description

    status = Column(String, default="todo")  
    # Task status: todo / in_progress / done

    priority = Column(Integer, default=1)  
    # Priority (you can later use this for heap/DSA logic)

    owner_id = Column(Integer, ForeignKey("users.id"))  
    # Foreign key linking task → user

    owner = relationship("User")  
    # SQLAlchemy relationship to access user object via task.owner