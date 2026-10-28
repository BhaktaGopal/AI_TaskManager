from fastapi import Depends, HTTPException, status
from app.core.dependencies import get_current_user
from app.core.roles import ADMIN


def require_roles(*roles):
    """
    This function returns a dependency function.
    It allows us to specify allowed roles dynamically.
    
    Example:
    Depends(require_roles("admin", "user"))
    """

    def role_checker(current_user = Depends(get_current_user)):
        # FastAPI will inject current_user automatically

        if current_user.role not in roles:
            # If user's role is not allowed → reject request
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        return current_user
        # Return user so it can still be used in route

    return role_checker
    # Return the dependency function itself