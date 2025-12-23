from sqlalchemy.orm import Session
from .models import Document, Query, IndexMetadata
from datetime import datetime
from typing import List, Optional

class DocumentCRUD:
    @staticmethod
    def create(db: Session, filename: str, original_filename: str, file_type: str, content: str, file_size: int):
        db_document = Document(
            filename=filename,
            original_filename=original_filename,
            file_type=file_type,
            content=content,
            file_size=file_size
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document
    
    @staticmethod
    def get(db: Session, document_id: str) -> Optional[Document]:
        return db.query(Document).filter(Document.id == document_id).first()
    
    @staticmethod
    def get_all(db: Session) -> List[Document]:
        return db.query(Document).all()
    
    @staticmethod
    def get_indexed(db: Session) -> List[Document]:
        return db.query(Document).filter(Document.indexed == True).all()
    
    @staticmethod
    def update_processed(db: Session, document_id: str, chunk_count: int):
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if db_document:
            db_document.processed = True
            db_document.chunk_count = chunk_count
            db_document.updated_at = datetime.utcnow()
            db.commit()
        return db_document
    
    @staticmethod
    def update_indexed(db: Session, document_id: str):
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if db_document:
            db_document.indexed = True
            db_document.updated_at = datetime.utcnow()
            db.commit()
        return db_document
    
    @staticmethod
    def delete(db: Session, document_id: str):
        db_document = db.query(Document).filter(Document.id == document_id).first()
        if db_document:
            db.delete(db_document)
            db.commit()
        return db_document


class QueryCRUD:
    @staticmethod
    def create(db: Session, document_id: str, question: str, answer: str, confidence: float, 
               latency_ms: float, retrieved_chunks: list, citations: list, support_details: list):
        db_query = Query(
            document_id=document_id,
            question=question,
            answer=answer,
            confidence=confidence,
            latency_ms=latency_ms,
            retrieved_chunks=retrieved_chunks,
            citations=citations,
            support_details=support_details
        )
        db.add(db_query)
        db.commit()
        db.refresh(db_query)
        return db_query
    
    @staticmethod
    def get(db: Session, query_id: str) -> Optional[Query]:
        return db.query(Query).filter(Query.id == query_id).first()
    
    @staticmethod
    def get_all_by_document(db: Session, document_id: str) -> List[Query]:
        return db.query(Query).filter(Query.document_id == document_id).all()
    
    @staticmethod
    def get_all(db: Session, limit: int = 100) -> List[Query]:
        return db.query(Query).order_by(Query.created_at.desc()).limit(limit).all()


class IndexMetadataCRUD:
    @staticmethod
    def create(db: Session, index_name: str, document_ids: list, total_chunks: int, index_size_mb: float):
        # Upsert logic: Check if exists first
        db_metadata = db.query(IndexMetadata).filter(IndexMetadata.index_name == index_name).first()
        
        if db_metadata:
            # Update existing
            db_metadata.document_ids = document_ids
            db_metadata.total_chunks = total_chunks
            db_metadata.index_size_mb = index_size_mb
            db_metadata.last_indexed = datetime.utcnow()
            db_metadata.updated_at = datetime.utcnow()
        else:
            # Create new
            db_metadata = IndexMetadata(
                index_name=index_name,
                document_ids=document_ids,
                total_chunks=total_chunks,
                index_size_mb=index_size_mb,
                last_indexed=datetime.utcnow()
            )
            db.add(db_metadata)
            
        try:
            db.commit()
            db.refresh(db_metadata)
        except Exception:
            db.rollback()
            raise
            
        return db_metadata
    
    @staticmethod
    def get_latest(db: Session) -> Optional[IndexMetadata]:
        return db.query(IndexMetadata).order_by(IndexMetadata.created_at.desc()).first()
    
    @staticmethod
    def update(db: Session, index_name: str, document_ids: list, total_chunks: int, index_size_mb: float):
        db_metadata = db.query(IndexMetadata).filter(IndexMetadata.index_name == index_name).first()
        if db_metadata:
            db_metadata.document_ids = document_ids
            db_metadata.total_chunks = total_chunks
            db_metadata.index_size_mb = index_size_mb
            db_metadata.last_indexed = datetime.utcnow()
            db_metadata.updated_at = datetime.utcnow()
            db.commit()
        return db_metadata