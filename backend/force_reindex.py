import sys
import os
import requests

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import config
from src.database.db import SessionLocal
from src.database.crud import DocumentCRUD, IndexMetadataCRUD
from src.modules.rag_system import TextChunker, Embedder, FAISSManager

def force_rebuild():
    print("Force Rebuilding Index...")
    
    db = SessionLocal()
    try:
        # Get all documents
        documents = DocumentCRUD.get_all(db)
        if not documents:
            print("No documents found in DB.")
            return

        print(f"Found {len(documents)} documents. Re-chunking...")

        # Initialize Components
        chunker = TextChunker(
            chunk_size=config.RAG_CONFIG['chunking']['chunk_size'],
            overlap=config.RAG_CONFIG['chunking']['overlap']
        )
        embedder = Embedder(config.RAG_CONFIG['embedding']['model_name'])

        all_chunks = []
        all_metadata = []

        import json

        for doc in documents:
            # Handle JSON content
            try:
                if doc.content.strip().startswith('['):
                    input_content = json.loads(doc.content)
                else:
                    input_content = doc.content
            except:
                input_content = doc.content

            # Chunk (Now uses clean logic from rag_system.py)
            chunks, metadatas = chunker.chunk(input_content)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                meta = {
                    'source_file': doc.original_filename,
                    'doc_id': doc.id,
                    'chunk_idx': i
                }
                if metadatas and i < len(metadatas):
                    meta.update(metadatas[i])
                all_metadata.append(meta)
            
            # Update DB status
            DocumentCRUD.update_processed(db, doc.id, len(chunks))
            DocumentCRUD.update_indexed(db, doc.id)

        print(f"Generated {len(all_chunks)} chunks. Embedding...")

        # Embed
        embeddings = embedder.embed(
            all_chunks,
            batch_size=config.RAG_CONFIG['embedding']['batch_size']
        )
        
        # Build Index
        index = FAISSManager.build_index(embeddings)
        
        # Save
        FAISSManager.save(index, all_chunks, all_metadata, str(config.INDEXES_DIR))
        
        # Update Metadata
        IndexMetadataCRUD.create(
            db,
            index_name="main_index",
            document_ids=[d.id for d in documents],
            total_chunks=len(all_chunks),
            index_size_mb=len(all_chunks) * 0.0001
        )
        
        print("Index Rebuild Complete!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    force_rebuild()
