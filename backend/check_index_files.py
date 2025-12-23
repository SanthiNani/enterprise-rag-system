import pickle
import json
from pathlib import Path
from config import config

indexes_dir = config.INDEXES_DIR
print(f"Checking indexes in {indexes_dir}")

# Check metadata.json
try:
    with open(indexes_dir / 'metadata.json', 'r') as f:
        meta = json.load(f)
    print("metadata.json: OK (Valid JSON)")
    print(f"Sample metadata: {meta[0] if meta else 'Empty'}")
except Exception as e:
    print(f"metadata.json: ERROR ({e})")

# Check chunks.pkl
try:
    with open(indexes_dir / 'chunks.pkl', 'rb') as f:
        chunks = pickle.load(f)
    print(f"chunks.pkl: OK ({len(chunks)} chunks)")
except Exception as e:
    print(f"chunks.pkl: ERROR ({e})")
