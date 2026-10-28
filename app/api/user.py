from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.core.rbac import require_roles
from app.core.roles import ADMIN
from app.services.user_service import get_all_users
from app.schemas.user import UserListResponse
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }


@router.get("/all", response_model=list[UserListResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(ADMIN))
    # Only admin can access user list
):
    return get_all_users(db)