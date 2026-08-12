from pydantic import BaseModel
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.ai.chat_orchestrator import process_chat_message

router = APIRouter(prefix="/chat", tags=["Conversational Chat Assistant"])

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    intent: str
    reply: str
    data: Dict[str, Any]

@router.post("", response_model=ChatResponse)
def chat_with_cinemate(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Conversational Chat Endpoint: Orchestrates multi-turn user intent flows (discover, select movie, find show, recommend seats, book).
    """
    return process_chat_message(db, payload.message, payload.session_id)
