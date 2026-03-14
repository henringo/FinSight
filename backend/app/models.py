from sqlalchemy import Column, String, Numeric, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Price(Base):
    __tablename__ = "prices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String, nullable=False, index=True)
    ts = Column(DateTime(timezone=True), nullable=False, index=True)
    open = Column(Numeric)
    high = Column(Numeric)
    low = Column(Numeric)
    close = Column(Numeric)
    volume = Column(Numeric)
    source = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Indicator(Base):
    __tablename__ = "indicators"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String, nullable=False, index=True)
    ts = Column(DateTime(timezone=True), nullable=False, index=True)
    ma20 = Column(Numeric)
    rsi14 = Column(Numeric)
    vol30d = Column(Numeric)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AISummary(Base):
    __tablename__ = "ai_summaries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticker = Column(String, nullable=False)
    bucket = Column(String, nullable=False)
    summary_text = Column(Text, nullable=False)
    model_version = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        {"schema": None},  # Supabase uses public schema
    )


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doc_type = Column(String)
    title = Column(String)
    content = Column(Text, nullable=False)
    embedding = Column(String)  # Stored as text, pgvector handles conversion
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class QACache(Base):
    __tablename__ = "qa_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_hash = Column(String, unique=True, nullable=False, index=True)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
