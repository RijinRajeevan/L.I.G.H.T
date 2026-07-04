from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .database import Base
import os

# Polyfill JSON column for SQLite fallback vs Postgres JSONB
if os.getenv("DATABASE_URL", "").startswith("postgresql"):
    from sqlalchemy.dialects.postgresql import JSONB as JSONColumnType
else:
    from sqlalchemy import JSON as JSONColumnType

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    user_query = Column(Text, nullable=False)
    
    # Store retrieved document IDs and similarity scores
    retrieved_documents = Column(JSONColumnType, nullable=True) 
    
    # Tools called by the LangGraph pipeline
    tools_invoked = Column(JSONColumnType, nullable=True)
    
    # Model configs
    model_parameters = Column(JSONColumnType, nullable=True)
    
    token_usage = Column(Integer, default=0)
    response_latency = Column(Float, nullable=True)
    
    final_answer = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    risk_level = Column(String(50), nullable=True)

class EscalationQueue(Base):
    __tablename__ = "escalation_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    user_query = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)
    risk_flag = Column(String(50), nullable=False)
    conflict_detected = Column(Boolean, default=False)
    
    status = Column(String(50), default="REQUIRES_REVIEW") # REQUIRES_REVIEW, REVIEWED, RESOLVED
    reviewer_notes = Column(Text, nullable=True)
