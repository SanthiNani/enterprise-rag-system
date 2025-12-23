import sys
import os
import json
import numpy as np
import argparse
from rouge_score import rouge_scorer
from sklearn.metrics import precision_score, recall_score

# Add parent dir to path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import config
from src.modules.rag_system import RAGSystem, FAISSManager
from src.modules.generator import Generator

def calculate_metrics(generated, reference):
    # ROUGE
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(reference, generated)
    rouge_l = scores['rougeL'].fmeasure
    
    # Simple Token Overlap for P/R (approximation without strict class labels)
    gen_tokens = set(generated.lower().split())
    ref_tokens = set(reference.lower().split())
    
    if not gen_tokens or not ref_tokens:
        return 0.0, 0.0, rouge_l
    
    overlap = len(gen_tokens.intersection(ref_tokens))
    precision = overlap / len(gen_tokens)
    recall = overlap / len(ref_tokens)
    
    return precision, recall, rouge_l

def run_eval():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', action='store_true', help='Run in baseline mode (no verification/reranking)')
    parser.add_argument('--auto', action='store_true', help='Use auto-generated test set')
    args = parser.parse_args()

    print(f"Initializing RAG Evaluation (Baseline Mode: {args.baseline})...")
    
    # Initialize Components
    try:
        # If Baseline, disable reranker/verification in config
        if args.baseline:
            config.RAG_CONFIG['retrieval']['use_reranker'] = False
            config.RAG_CONFIG['verification']['confidence_threshold'] = 0.0 # Accept everything
            print(">> BASELINE CONFIG APPLIED: No Reranker, No Verification Threshold.")

        # Inject API Key into config for RAGSystem to detect Gemini
        rag_config = config.RAG_CONFIG.copy()
        rag_config['GEMINI_API_KEY'] = config.GEMINI_API_KEY
        
        rag = RAGSystem(rag_config)
        if args.baseline:
            rag.reranker = None # Force disable 
        
        # Load Index
        index, chunks, metadata = FAISSManager.load(str(config.INDEXES_DIR))
        rag.index = index
        rag.chunks = chunks
        rag.metadata = metadata
        
        # Generator is handled inside RAGSystem now
        generator = None
        
    except Exception as e:
        print(f"Setup Error: {e}")
        return

    # Load Test Set
    filename = 'test_set_auto.json' if args.auto else 'test_set.json'
    test_set_path = os.path.join(os.path.dirname(__file__), filename)
    
    if not os.path.exists(test_set_path):
        print(f"Error: {filename} not found.")
        return
        
    with open(test_set_path, 'r') as f:
        test_set = json.load(f)
        
    results = []
    print(f"\nDtoing evaluation on {len(test_set)} items from {filename}...")
    
    for item in test_set:
        query = item.get('question', '')
        reference = item.get('reference_answer', '')
        
        if not query: continue

        print(f"\nProcessing Q: {query[:50]}...")
        
        try:
            # RAG Pipeline
            query_emb = rag.embedder.embed(query)[0]
            indices, distances = FAISSManager.search(rag.index, query_emb, k=config.RAG_CONFIG['retrieval']['k_retrieve'])
            
            retrieved_chunks = [rag.chunks[i] for i in indices]
            chunk_metadata_list = [rag.metadata[i] for i in indices]
            
            response = rag.answer_question(query, retrieved_chunks, chunk_metadata_list, generator)
            
            answer_text = response['answer']
            confidence = response['confidence']
            
            # Metrics
            precision, recall, rouge = calculate_metrics(answer_text, reference)
            
            print(f"  -> Conf: {confidence:.2f} | ROUGE-L: {rouge:.2f}")
            
            results.append({
                'q_id': item.get('q_id'),
                'question': query,
                'answer': answer_text,
                'reference': reference,
                'confidence': confidence,
                'metrics': {
                    'precision': precision,
                    'recall': recall,
                    'rouge_l': rouge
                }
            })
            
        except Exception as e:
            print(f"Error: {e}")

    # Summary
    if results:
        valid_results = [r for r in results if 'metrics' in r]
        avg_conf = np.mean([r['confidence'] for r in results])
        avg_prec = np.mean([r['metrics']['precision'] for r in valid_results])
        avg_rec = np.mean([r['metrics']['recall'] for r in valid_results])
        avg_rouge = np.mean([r['metrics']['rouge_l'] for r in valid_results])
        
        print("\n" + "="*40)
        print(f"EVALUATION SUMMARY (Baseline: {args.baseline})")
        print("="*40)
        print(f"Grounding (Avg Conf): {avg_conf:.2%}")
        print(f"Precision: {avg_prec:.2%}")
        print(f"Recall: {avg_rec:.2%}")
        print(f"ROUGE-L: {avg_rouge:.2%}")
        print("="*40)
        
        out_name = f'results_{"baseline" if args.baseline else "rag"}.json'
        out_path = os.path.join(os.path.dirname(__file__), out_name)
        with open(out_path, 'w') as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_eval()
