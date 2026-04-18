from fastapi import APIRouter, Depends,status, HTTPException
from sqlalchemy.orm import Session
import uuid
from typing import Optional

from ..database import get_db
from ..auth_utils import get_current_user
from ..models import User,ChatSession,Message
from ..agents.pipeline import run_research_pipeline

router =APIRouter(prefix="/research",tags=["Research"])
@router.post("/start")
async def start_research(
    topic: str,
    session_id: Optional[uuid.UUID] = None,   # <-- add this
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # If session_id given, continue old chat — else create new
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user.id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(
            id=uuid.uuid4(),
            user_id=current_user.id,
            title=f"Research: {topic[:30]}..."
        )
        db.add(session)

    user_msg = Message(session_id=session.id, role="user", content=topic)
    db.add(user_msg)
    db.commit()

    try:
        result = run_research_pipeline(topic=topic)
        agent_msg = Message(session_id=session.id, role="assistant", content=result["report"])
        db.add(agent_msg)
        db.commit()
        return {"session_id": session.id, "report": result["report"]}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
# GET all sessions of logged-in user (sidebar ke liye)
@router.get("/sessions")
def get_all_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.created_at.desc()).first()  # Latest first
    
    return [{"id": str(s.id), "title": s.title} for s in sessions]

# DELETE a session
@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    db.commit()
    return {"message": "Session deleted"}
@router.get("/sessions/{session_id}/messages")
def get_session_messages(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check  session is this is same logged-in user or not 
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Session not found or unauthorized"
        )
    
    return session.messages