# ============================================================================
# FILE: backend/src/database/models.py
# ============================================================================

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf, txt, docx
    file_size = Column(Integer)
    content = Column(Text)
    processed = Column(Boolean, default=False)
    indexed = Column(Boolean, default=False)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    queries = relationship("Query", back_populates="document")


class Query(Base):
    __tablename__ = "queries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"))
    question = Column(Text, nullable=False)
    answer = Column(Text)
    confidence = Column(Float)
    latency_ms = Column(Float)
    retrieved_chunks = Column(JSON)
    citations = Column(JSON)
    support_details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    document = relationship("Document", back_populates="queries")


class IndexMetadata(Base):
    __tablename__ = "index_metadata"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    index_name = Column(String(255), unique=True, nullable=False)
    document_ids = Column(JSON)  # List of document IDs
    total_chunks = Column(Integer, default=0)
    index_size_mb = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_indexed = Column(DateTime)