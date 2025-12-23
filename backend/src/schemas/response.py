from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class QueryResponse(BaseModel):
    question: str
    answer: str
    confidence: float
    citations: List[Dict]
    latency_ms: float
    retrieved_chunks: List[str]
    support_details: List[Dict]

class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    processed: bool
    indexed: bool
    chunk_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    total: int
    documents: List[DocumentResponse]

class IndexStatusResponse(BaseModel):
    index_exists: bool
    total_documents: int
    total_chunks: int
    index_size_mb: float
    last_updated: Optional[datetime]

class HealthResponse(BaseModel):
    status: str
    database: str
    models_loaded: bool
    version: str