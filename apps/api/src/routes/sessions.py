"""Sessions and Feedback routes."""
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timezone
import uuid

router = APIRouter()


class SessionCreateRequest(BaseModel):
    user_id: str


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    created_at: str


@router.post("/sessions", response_model=SessionResponse, tags=["sessions"])
async def create_session(request: SessionCreateRequest) -> SessionResponse:
    return SessionResponse(
        session_id=str(uuid.uuid4()),
        user_id=request.user_id,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
