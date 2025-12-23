import pickle
from pathlib import Path

index_dir = Path("data/indexes")
chunks_path = index_dir / "chunks.pkl"

if not chunks_path.exists():
    print("Chunks file not found.")
    exit()

with open(chunks_path, 'rb') as f:
    chunks = pickle.load(f)

print(f"Total chunks: {len(chunks)}")
print("Searching for 'Section 6'...")

found = False
for i, chunk in enumerate(chunks):
    if "section 6" in chunk.lower():
        print(f"\n[Chunk {i}]:")
        print(chunk)
        found = True

if not found:
    print("Text 'Section 6' NOT found in any chunk.")
