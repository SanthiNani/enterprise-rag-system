from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config import config
from src.database.db import init_db, get_db, engine
from src.database.crud import DocumentCRUD, QueryCRUD, IndexMetadataCRUD
from src.database.models import Base
from src.database.models import Base
from src.modules.rag_system import RAGSystem, FAISSManager, TextChunker, Embedder, GeminiGenerator
from src.modules.generator import Generator
from src.schemas.response import (
    QueryResponse, DocumentResponse, DocumentListResponse, 
    IndexStatusResponse, HealthResponse
)
from pathlib import Path
import shutil
from typing import List
import logging
import json
import io
import pdfplumber
import docx
import os

# Setup logging
level=config.LOG_LEVEL,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
handlers=[
    logging.StreamHandler(),
    logging.FileHandler(config.DATA_DIR / 'app.log')
    ]

logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="RAG System API",
    description="Retrieval-Augmented Generation System with Answer Verification",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
# Global components
rag_components = {
    "rag": None,
    "embedder": None,
    "generator": None,
    "index_data": None  # (index, chunks, metadata)
}

# Initialize components on startup
@app.on_event("startup")
async def startup():
    init_db()
    logger.info("Database initialized")
    
    try:
        logger.info("Loading RAG models...")
        rag_components["rag"] = RAGSystem(config.RAG_CONFIG)
        rag_components["embedder"] = Embedder(config.RAG_CONFIG['embedding']['model_name'])
        
        if config.GEMINI_API_KEY:
            logger.info("Initializing connected Gemini Generator")
            rag_components["generator"] = GeminiGenerator(config.GEMINI_API_KEY, config.RAG_CONFIG['generation']['model_name'])
        else:
            logger.info("Initializing local T5 Generator")
            rag_components["generator"] = Generator(config.RAG_CONFIG['generation']['model_name'])
        
        # Try to load index if exists
        if (config.INDEXES_DIR / 'index.bin').exists():
            rag_components["index_data"] = FAISSManager.load(str(config.INDEXES_DIR))
            logger.info("FAISS index loaded")
            
        logger.info("All RAG models loaded successfully")
    except Exception as e:
        logger.error(f"Error loading RAG models: {str(e)}")

# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "models_loaded": True,
        "version": "1.0.0"
    }

# ============ DOCUMENT ENDPOINTS ============

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a document"""
    try:
        # Read file
        content = await file.read()
        file_ext = file.filename.split('.')[-1].lower()
        
        # Save file locally
        file_path = config.RAW_DIR / file.filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Extract text based on file type
        text_content = ""
        
        if file_ext == 'pdf':
            pages_data = []
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        pages_data.append({
                            'text': text,
                            'page': i + 1
                        })
            text_content = json.dumps(pages_data, ensure_ascii=False)
                
        elif file_ext == 'docx':
            # DOCX usually doesn't have fixed "pages" in the same way, but we can treat paragraphs as a single block for now
            # Or just legacy extraction
            doc = docx.Document(io.BytesIO(content))
            full_text = ""
            for para in doc.paragraphs:
                full_text += para.text + "\n"
            text_content = full_text
                
        elif file_ext == 'txt':
            text_content = content.decode('utf-8', errors='ignore')
            
        else:
            # Fallback for other types
            text_content = content.decode('utf-8', errors='ignore')

        # Sanitize text: Remove NUL bytes which cause Postgres errors
        text_content = text_content.replace('\x00', '')
        
        # Save to database
        document = DocumentCRUD.create(
            db,
            filename=str(file_path),
            original_filename=file.filename,
            file_type=file_ext,
            content=text_content,
            file_size=len(content)
        )
        
        logger.info(f"Document uploaded: {file.filename}")
        return {"document_id": document.id, "filename": file.filename}
    
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents", response_model=DocumentListResponse)
async def get_documents(db: Session = Depends(get_db)):
    """Get all documents"""
    documents = DocumentCRUD.get_all(db)
    return {
        "total": len(documents),
        "documents": documents
    }


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document"""
    try:
        DocumentCRUD.delete(db, document_id)
        logger.info(f"Document deleted: {document_id}")
        return {"message": "Document deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ INDEX ENDPOINTS ============

from fastapi import BackgroundTasks
from src.database.db import SessionLocal

def process_index_build():
    """Background task for building index"""
    logger.info("Starting background index build...")
    db = SessionLocal()
    try:
        # Get all documents
        documents = DocumentCRUD.get_all(db)
        if not documents:
            logger.warning("No documents to index")
            return
        
        # Chunk documents
        chunker = TextChunker(
            chunk_size=config.RAG_CONFIG['chunking']['chunk_size'],
            overlap=config.RAG_CONFIG['chunking']['overlap']
        )
        
        all_chunks = []
        all_metadata = []
        
        for doc in documents:
            # Check if content is JSON (new format) or string (old format)
            try:
                if doc.content.strip().startswith('['):
                    input_content = json.loads(doc.content)
                else:
                    input_content = doc.content
            except:
                input_content = doc.content

            chunks, metadatas = chunker.chunk(input_content)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                
                # Base metadata
                meta = {
                    'source_file': doc.original_filename,
                    'doc_id': doc.id,
                    'chunk_idx': i
                }
                
                # Add specific page metadata if available
                if metadatas and i < len(metadatas):
                    meta.update(metadatas[i])
                    
                all_metadata.append(meta)
            
            DocumentCRUD.update_processed(db, doc.id, len(chunks))
        
        # Generate embeddings
        embedder = Embedder(config.RAG_CONFIG['embedding']['model_name'])
        embeddings = embedder.embed(
            all_chunks,
            batch_size=config.RAG_CONFIG['embedding']['batch_size']
        )
        
        # Build FAISS index
        index = FAISSManager.build_index(embeddings)
        
        # Save index
        FAISSManager.save(index, all_chunks, all_metadata, str(config.INDEXES_DIR))
        
        # Update database
        for doc in documents:
            DocumentCRUD.update_indexed(db, doc.id)
        
        IndexMetadataCRUD.create(
            db,
            index_name="main_index",
            document_ids=[d.id for d in documents],
            total_chunks=len(all_chunks),
            index_size_mb=len(all_chunks) * 0.0001  # Rough estimate
        )
        
        logger.info(f"Index built successfully with {len(all_chunks)} chunks")
        
    except Exception as e:
        logger.error(f"Error building index: {str(e)}")
    finally:
        db.close()


@app.post("/api/index/build")
async def build_index(background_tasks: BackgroundTasks):
    """Trigger background index build"""
    background_tasks.add_task(process_index_build)
    return {"message": "Index build started", "status": "processing"}


@app.get("/api/index/status", response_model=IndexStatusResponse)
async def get_index_status(db: Session = Depends(get_db)):
    """Get index status"""
    try:
        index_path = config.INDEXES_DIR / 'index.bin'
        index_exists = index_path.exists()
        
        if not index_exists:
            return {
                "index_exists": False,
                "total_documents": 0,
                "total_chunks": 0,
                "index_size_mb": 0,
                "last_updated": None
            }
        
        metadata = IndexMetadataCRUD.get_latest(db)
        
        return {
            "index_exists": True,
            "total_documents": len(metadata.document_ids) if metadata else 0,
            "total_chunks": metadata.total_chunks if metadata else 0,
            "index_size_mb": metadata.index_size_mb if metadata else 0,
            "last_updated": metadata.last_indexed if metadata else None
        }
    
    except Exception as e:
        logger.error(f"Error getting index status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ QUERY ENDPOINTS ============

@app.post("/api/query/answer", response_model=QueryResponse)
def answer_query(
    question: str,
    db: Session = Depends(get_db)
):
    """Answer a question using RAG (Run in threadpool)"""
    try:
        index_path = config.INDEXES_DIR / 'index.bin'
        if not index_path.exists():
            raise HTTPException(status_code=400, detail="Index not built. Please build index first.")
        
        # Check if components are loaded
        if not rag_components["generator"]:
             raise HTTPException(status_code=503, detail="RAG system not initialized")
             
        # Auto-reload index if file changed on disk
        current_mtime = os.path.getmtime(index_path)
        last_mtime = rag_components.get("index_mtime", 0)
        
        if not rag_components["index_data"] or current_mtime > last_mtime:
             logger.info(f"Reloading index (mtime: {current_mtime} > {last_mtime})")
             rag_components["index_data"] = FAISSManager.load(str(config.INDEXES_DIR))
             rag_components["index_mtime"] = current_mtime
        
        index, chunks, metadata = rag_components["index_data"]
        
        rag = rag_components["rag"]
        embedder = rag_components["embedder"]
        generator = rag_components["generator"]
        
        # Retrieve
        query_embedding = embedder.embed(question)[0]
        indices, distances = FAISSManager.search(index, query_embedding, config.RAG_CONFIG['retrieval']['k_retrieve'])
        
        retrieved_chunks = [chunks[i] for i in indices]
        retrieved_metadata = [metadata[i] for i in indices]
        
        # Answer with LLM
        result = rag.answer_question(question, retrieved_chunks, retrieved_metadata, generator)
        
        # Save to database (Safe Save)
        try:
            doc_id_ref = retrieved_metadata[0].get('doc_id') if retrieved_metadata else None
            # Verify if doc exists to prevent FK violation (Extra Safety)
            if doc_id_ref:
                existing_doc = DocumentCRUD.get(db, doc_id_ref)
                if not existing_doc:
                    logger.warning(f"Document {doc_id_ref} referenced in index but not found in DB. Saving query as orphan.")
                    doc_id_ref = None

            query_record = QueryCRUD.create(
                db,
                document_id=doc_id_ref,
                question=question,
                answer=result['answer'],
                confidence=result['confidence'],
                latency_ms=result['latency']['total_ms'],
                retrieved_chunks=result['retrieved_chunks'],
                citations=result['citations'],
                support_details=result['support_details']
            )
        except Exception as e:
            logger.error(f"Error saving query record: {str(e)}")
            # Continue anyway, don't fail the request just because logging failed
        
        return {
            "question": question,
            "answer": result['answer'],
            "confidence": result['confidence'],
            "citations": result['citations'],
            "latency_ms": result['latency']['total_ms'],
            "retrieved_chunks": result['retrieved_chunks'],
            "support_details": result['support_details']
        }
    
    except Exception as e:
        logger.error(f"Error answering query: {str(e)}")
        # Log full traceback for debugging
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/query/history")
async def get_query_history(db: Session = Depends(get_db), limit: int = 50):
    """Get query history"""
    queries = QueryCRUD.get_all(db, limit)
    return {"total": len(queries), "queries": queries}

@app.get("/api/evaluation/results")
async def get_evaluation_results():
    """Get latest evaluation results"""
    try:
        base_path = Path("evaluation")
        rag_path = base_path / "results_rag.json"
        baseline_path = base_path / "results_baseline.json"
        
        results = {
            "rag": None,
            "baseline": None,
            "summary": {}
        }
        
        if rag_path.exists():
            with open(rag_path, 'r') as f:
                data = json.load(f)
                results["rag"] = data
                # Calc summary on the fly if not in file
                valid = [r for r in data if 'metrics' in r]
                if valid:
                    results["summary"] = {
                        "rag_precision": sum(r['metrics']['precision'] for r in valid)/len(valid),
                        "rag_recall": sum(r['metrics']['recall'] for r in valid)/len(valid),
                        "rag_rouge": sum(r['metrics']['rouge_l'] for r in valid)/len(valid),
                        "rag_confidence": sum(r['confidence'] for r in data)/len(data)
                    }

        if baseline_path.exists():
            with open(baseline_path, 'r') as f:
                data = json.load(f)
                results["baseline"] = data
                valid = [r for r in data if 'metrics' in r]
                if valid:
                    results["summary"].update({
                        "baseline_precision": sum(r['metrics']['precision'] for r in valid)/len(valid),
                        "baseline_recall": sum(r['metrics']['recall'] for r in valid)/len(valid), 
                        "baseline_rouge": sum(r['metrics']['rouge_l'] for r in valid)/len(valid)
                    })

        return results
    except Exception as e:
        logger.error(f"Error fetching evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)