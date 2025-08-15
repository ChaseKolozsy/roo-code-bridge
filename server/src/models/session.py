from typing import Dict, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
import asyncio
from sqlalchemy import Column, String, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Session(BaseModel):
    id: str
    client_id: str
    created_at: datetime
    last_activity: datetime
    active: bool
    context: dict
    provider: Optional[str] = "roo-code"
    
class SessionRecord(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True)
    client_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)
    context = Column(JSON, default=dict)
    provider = Column(String, default="roo-code")

class SessionManager:
    _sessions: Dict[str, Session] = {}
    _lock = asyncio.Lock()
    
    @classmethod
    async def create_session(cls, client_id: str, provider: str = "roo-code") -> Session:
        async with cls._lock:
            session_id = str(uuid.uuid4())
            session = Session(
                id=session_id,
                client_id=client_id,
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                active=True,
                context={},
                provider=provider
            )
            cls._sessions[session_id] = session
            return session
    
    @classmethod
    async def get_session(cls, session_id: str) -> Optional[Session]:
        return cls._sessions.get(session_id)
    
    @classmethod
    async def update_activity(cls, session_id: str):
        if session_id in cls._sessions:
            cls._sessions[session_id].last_activity = datetime.utcnow()
    
    @classmethod
    def close_session(cls, session_id: str):
        if session_id in cls._sessions:
            cls._sessions[session_id].active = False
    
    @classmethod
    async def cleanup_inactive(cls, timeout_minutes: int = 30):
        async with cls._lock:
            cutoff = datetime.utcnow() - timedelta(minutes=timeout_minutes)
            inactive_sessions = [
                sid for sid, session in cls._sessions.items()
                if session.last_activity < cutoff
            ]
            for sid in inactive_sessions:
                cls.close_session(sid)
                del cls._sessions[sid]
    
    @classmethod
    async def cleanup_all(cls):
        async with cls._lock:
            for session_id in list(cls._sessions.keys()):
                cls.close_session(session_id)
            cls._sessions.clear()
    
    @classmethod
    def get_active_sessions(cls) -> List[Session]:
        return [s for s in cls._sessions.values() if s.active]