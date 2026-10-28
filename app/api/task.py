from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.core.dependencies import get_current_user
from app.models.task import Task
from app.schemas.task import  TaskUpdate,TaskAssignCreate, TaskReassign
from app.services.task_service import  get_tasks, update_task, delete_task, create_and_assign_task, reassign_task
from app.core.rbac import require_roles
from app.core.roles import USER, ADMIN

router = APIRouter(prefix="/tasks", tags=["Tasks"])
# All routes under /tasks
# Create TASK
@router.post("/")
def create_new_task(
    data: TaskAssignCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(USER, ADMIN))
):
    return create_and_assign_task(db, data)

# Update TASK
@router.put("/{task_id}")
def update_existing_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    # Fetch task from DB

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        # Only owner or admin can update

    return update_task(db, task, data)

# Delete TASK
@router.delete("/{task_id}")
def delete_existing_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    delete_task(db, task)

    return {"message": "Task deleted"}

    
# Get TASKS
@router.get("/all")
def get_all_tasks(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(ADMIN))
    # Only admin can access
):
    return db.query(Task).all()
# GET FOR CURRENT USER
@router.get("/current")
def get_current_user_tasks(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(USER,ADMIN))
):
    return get_tasks(db, current_user)

# REASSIGNING THE EXISTING TASK
@router.put("/{task_id}/assign")
def reassign_existing_task(
    task_id: int,
    data: TaskReassign,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(ADMIN))
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return reassign_task(db, task, data.user_id)