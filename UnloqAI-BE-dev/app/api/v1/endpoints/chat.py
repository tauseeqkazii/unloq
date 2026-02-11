from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import uuid

from app.db.session import get_db
from app.models.meridian import ChatSession, ChatMessage
from app.services.meridian.copilot import CopilotService

router = APIRouter()

# --- Schemas ---
class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Chat"

class MessageRequest(BaseModel):
    content: str # The user's question

class SessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: str

# --- Endpoints ---

# 1. List All Chats (Sidebar)
@router.get("/sessions", response_model=List[SessionResponse])
def get_sessions(db: Session = Depends(get_db)):
    # In real auth, filter by current_user.id
    sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
    return [
        {
            "session_id": str(s.session_id),
            "title": s.title,
            "created_at": s.created_at.isoformat()
        } 
        for s in sessions
    ]

# 2. Create New Chat (The "+" Button)
@router.post("/sessions", response_model=SessionResponse)
def create_session(req: CreateSessionRequest, db: Session = Depends(get_db)):
    # Default user for demo
    new_session = ChatSession(title=req.title, user_id="demo_user")
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {
        "session_id": str(new_session.session_id),
        "title": new_session.title,
        "created_at": new_session.created_at.isoformat()
    }

# 3. Get Chat History (Load a conversation)
@router.get("/sessions/{session_id}/messages")
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    # Validate UUID format to prevent 500
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    msgs = db.query(ChatMessage)\
             .filter(ChatMessage.session_id == sid)\
             .order_by(ChatMessage.created_at.asc())\
             .all()
    
    return [
        {"id": str(m.id), "role": m.role, "content": m.content} 
        for m in msgs
    ]

# 4. Send Message & Stream Response (The "Enter" Key)
@router.post("/sessions/{session_id}/message")
async def send_message(
    session_id: str, 
    req: MessageRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # 1. Verify Session
    session = db.query(ChatSession).filter(ChatSession.session_id == sid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. Save User Message
    user_msg = ChatMessage(
        session_id=sid,
        role="user",
        content=req.content
    )
    db.add(user_msg)
    
    # 3. Update Session Timestamp (brings it to top of list)
    session.updated_at = datetime.utcnow()
    db.commit()

    # 4. Initialize Service with Session Context
    service = CopilotService(db, str(sid))
    
    # 5. Auto-Title Generation (If it's the first message)
    # We do this in background to not block the stream
    msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == sid).count()
    if msg_count <= 2: 
        background_tasks.add_task(service.generate_title, str(sid), req.content)

    # 6. Stream Response
    return StreamingResponse(
        service.chat_completion(req.content),
        media_type="text/plain"
    )


class UpdateSessionRequest(BaseModel):
    title: str

@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    try:
        sid = uuid.UUID(session_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid UUID")
        
    session = db.query(ChatSession).filter(ChatSession.session_id == sid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session) # Cascades to messages
    db.commit()
    return {"status": "deleted", "id": session_id}

@router.patch("/sessions/{session_id}")
def rename_session(session_id: str, req: UpdateSessionRequest, db: Session = Depends(get_db)):
    try:
        sid = uuid.UUID(session_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid UUID")

    session = db.query(ChatSession).filter(ChatSession.session_id == sid).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    session.title = req.title
    db.commit()
    return {"status": "updated", "title": session.title}