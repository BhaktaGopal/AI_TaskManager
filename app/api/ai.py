from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.core.dependencies import get_current_user
from app.genai.rag_service import query_tasks

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/query")
def ask_ai(
    request: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    AI endpoint for querying tasks using RAG
    """

    user_query = request.get("query")
    # Extract query from request body

    if not user_query:
        return {"error": "Query is required"}
        # Basic validation

    result = query_tasks(db, current_user.id, user_query)
    # Call RAG service

    return {"response": result}
    # Return result