from src.database.db import SessionLocal
from src.database.models import Document
import random

db = SessionLocal()
docs = db.query(Document).all()

print(f"Found {len(docs)} documents.")
for doc in docs:
    print(f"\n{'='*50}")
    print(f"Document: {doc.original_filename} (ID: {doc.id})")
    print(f"Total Length: {len(doc.content)} chars")
    
    # Check start
    print(f"\n--- Start (First 500 chars) ---")
    print(doc.content[:500])
    
    # Check middle (to see if it's just headers/footers repeats)
    if len(doc.content) > 2000:
        mid_start = len(doc.content) // 2
        print(f"\n--- Middle (500 chars at {mid_start}) ---")
        print(doc.content[mid_start:mid_start+500])
    
    # Check for common garbage
    garbage_indicators = ['\x00', '', '(cid:']
    found_garbage = [g for g in garbage_indicators if g in doc.content]
    if found_garbage:
        print(f"\n[WARNING] Found potential garbage characters: {found_garbage}")

db.close()
