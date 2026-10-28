from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.user import User

def create_and_assign_task(db, data):
    # Validate if target user exists
    user = db.query(User).filter(User.id == data.user_id).first()

    if not user:
        raise Exception("User not found")
        # Prevent assigning to invalid user

    task = Task(
        title=data.title,
        description=data.description,
        priority=data.priority,
        owner_id=data.user_id  
        # Assign directly to given user
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task
# def create_task(db: Session, user_id: int, data):
#     task = Task(
#         title=data.title,
#         description=data.description,
#         priority=data.priority,
#         owner_id=user_id
#     )
#     # Create Task object and assign it to current user

#     db.add(task)  
#     # Add to session (not yet saved)

#     db.commit()  
#     # Save changes to database

#     db.refresh(task)  
#     # Refresh object to get updated values (like id)

#     return task
def reassign_task(db, task: Task, new_user_id: int):
    user = db.query(User).filter(User.id == new_user_id).first()

    if not user:
        raise Exception("User not found")

    task.owner_id = new_user_id  
    # Change ownership

    db.commit()
    db.refresh(task)

    return task


def get_tasks(db: Session, user):
    if user.role == "admin":
        return db.query(Task).all()  
        # Admin can see all tasks

    return db.query(Task).filter(Task.owner_id == user.id).all()  
    # Normal user → only their tasks


def update_task(db: Session, task: Task, data):
    for key, value in data.dict(exclude_unset=True).items():
        setattr(task, key, value)
        # Dynamically update only provided fields

    db.commit()  
    # Save updates

    db.refresh(task)  
    # Get latest state

    return task


def delete_task(db: Session, task: Task):
    db.delete(task)  
    # Mark task for deletion

    db.commit()  
    # Remove from DB