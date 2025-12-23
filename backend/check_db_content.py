from src.database.db import SessionLocal
from src.database.models import Document

db = SessionLocal()
docs = db.query(Document).all()

print(f"Found {len(docs)} documents.")
for doc in docs:
    print(f"\n--- Document: {doc.original_filename} (ID: {doc.id}) ---")
    print(f"Content Length: {len(doc.content)}")
    print(f"First 500 chars:\n{doc.content[:500]}")
    print("-" * 50)

db.close()
