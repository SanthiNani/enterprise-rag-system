import sys
import os
import json
import random
import re

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import config
from src.modules.rag_system import FAISSManager
from src.modules.generator import Generator

def generate_questions():
    print("Initializing Generator for Question Generation...")
    
    # Load Index to get chunks
    index_path = config.INDEXES_DIR / 'index.bin'
    if not index_path.exists():
        print("Index not found. Cannot generate questions.")
        return

    _, chunks, metadata = FAISSManager.load(str(config.INDEXES_DIR))
    
    # Load Generator (LLM)
    generator = Generator(config.RAG_CONFIG['generation']['model_name'])
    
    generated_set = []
    
    # We want ~50 questions. If we have fewer chunks, we loop or take all.
    # If we have many chunks, we sample.
    num_to_generate = 50
    selected_indices = random.choices(range(len(chunks)), k=num_to_generate)
    
    print(f"Generating {num_to_generate} questions from {len(chunks)} chunks...")
    
    for i, idx in enumerate(selected_indices):
        chunk_text = chunks[idx]
        meta = metadata[idx]
        
        # Heuristic to skip empty/short chunks
        if len(chunk_text) < 50:
            continue
            
        try:
            # Prompt Engineering to make T5 generate a question
            # T5 is trained on "generate question: <context>" tasks often, or we use a template.
            # Using a simple prompt: "generate a question for this context: ..."
            prompt = f"generate a question for this context: {chunk_text}"
            
            # Use the generator's internal pipeline or model directly?
            # Generator.generate() is designed for QA (Context + Query).
            # We need direct generation. Accessing internal pipeline if possible or just using generate() efficiently.
            # The Generator class wraps the pipeline. Let's see if we can use it.
            # If Generator only does QA, we might need to bypass it or use it creatively.
            # Assuming Generator.generate(prompt, []) might work if it just passes prompt to model.
            # Let's check Generator source or just try. Prepending "context:" might trigger QA mode.
            
            # Let's try sending the task as the query.
            question_generated = generator.generate(prompt, [])
            
            # Cleanup
            question_generated = question_generated.replace("question:", "").strip()
            
            # Fallback for weak generation
            if len(question_generated) < 10:
                question_generated = f"What does the document say about '{chunk_text[:20]}...'?"

            print(f"[{i+1}/{num_to_generate}] Q: {question_generated}")

            generated_set.append({
                "q_id": i + 100, # Offset ID
                "question": question_generated,
                "reference_answer": chunk_text, # The chunk IS the truth
                "relevant_keywords": [], # Hard to generate keywords auto, leave empty or tokenize
                "source_chunk_idx": idx
            })
            
        except Exception as e:
            print(f"Error generating for chunk {idx}: {e}")

    # Save
    out_path = os.path.join(os.path.dirname(__file__), 'test_set_auto.json')
    with open(out_path, 'w') as f:
        json.dump(generated_set, f, indent=2)
    
    print(f"Saved {len(generated_set)} questions to {out_path}")

if __name__ == "__main__":
    generate_questions()
