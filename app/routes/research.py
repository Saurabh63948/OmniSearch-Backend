from fastapi import APIRouter, Depends,status, HTTPException
from sqlalchemy.orm import Session
import uuid

from ..database import get_db
from ..auth_utils import get_current_user
from ..models import User,ChatSession,Message
from ..agents.pipeline import run_research_pipeline

router =APIRouter(prefix="/research",tags=["Research"])
@router.post("/start")
async def start_research(
  topic:str,
  db:Session =Depends(get_db),
  current_user:User =Depends(get_current_user)
):
  #1 create a new session 
  new_session =ChatSession(
    id=uuid.uuid4(),
    user_id=current_user.id,
    title=f"Research: {topic[:30]}..."
  )
  db.add(new_session)

  #2 save user prompt
  user_msg=Message(
    session_id=new_session.id,
    role="user",
    content=topic
  )
  db.add(user_msg)
  db.commit()
  try:
    #3. run agent pipeline
    result =run_research_pipeline(topic=topic)

    #4 store the final report of the agent
    agent_msg=Message(
      session_id=new_session.id,
      role="assistant",
      content=result["report"]
    )
    db.add(agent_msg)
    db.commit()
    return {
      "session_id":new_session.id,
      "report":result["report"]
    }
  
  except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500,detail =str(e))

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