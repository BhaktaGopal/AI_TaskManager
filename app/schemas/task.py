from pydantic import BaseModel


class TaskAssignCreate(BaseModel):
    title: str
    description: str | None = None
    priority: int = 1
    user_id: int 
    # Admin specifies which user to assign task to


class TaskReassign(BaseModel):
    user_id: int  
    # Only need new user_id for reassignment


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: int | None = None
    # All fields optional → partial update allowed


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    priority: int

    class Config:
        from_attributes = True  
        # Allows returning SQLAlchemy model directly