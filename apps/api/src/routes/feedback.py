"""Feedback collection routes."""
from fastapi import APIRouter
from src.schemas.cognitive import FeedbackRequest

router = APIRouter()


@router.post("/feedback", tags=["feedback"])
async def submit_feedback(request: FeedbackRequest) -> dict:
    """Store user feedback for pipeline improvement and reflection engine."""
    # In production: persist to PostgreSQL and trigger reflection engine update
    return {
        "received": True,
        "session_id": request.session_id,
        "rating": request.rating,
    }
