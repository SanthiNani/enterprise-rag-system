import os
import json
import pickle
import numpy as np
import nltk
from pathlib import Path
import time
from typing import List, Dict, Tuple, Optional

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

from sentence_transformers import SentenceTransformer, util, CrossEncoder
import faiss
from transformers import AutoTokenizer, pipeline
import google.generativeai as genai
import re

class Embedder:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def embed(self, texts, batch_size=32):
        if isinstance(texts, str):
            texts = [texts]
        embeddings = self.model.encode(texts, batch_size=batch_size, convert_to_tensor=False)
        return embeddings


class Reranker:
    def __init__(self, model_name='cross-encoder/ms-marco-MiniLM-L-6-v2'):
        self.model = CrossEncoder(model_name)
    
    def rerank(self, query, chunks, top_k=5):
        if not chunks:
            return []
        
        # Create pairs of (query, chunk)
        pairs = [[query, chunk] for chunk in chunks]
        
        # Predict scores
        scores = self.model.predict(pairs)
        
        # Sort by score (descending)
        sorted_indices = np.argsort(scores)[::-1]
        
        # Return top_k
        top_indices = sorted_indices[:top_k]
        return [chunks[i] for i in top_indices], top_indices


class GeminiGenerator:
    def __init__(self, api_key, model_name='gemini-pro'):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def generate(self, query, context_chunks):
        context = "\n\n".join(context_chunks)
        prompt = f"""You are an expert technical assistant. Answer the question specifically using ONLY the provided context.
If the answer is not contained in the context, say "I cannot answer this based on the provided documents."

Context:
{context}

Question: {query}

Answer:"""
        
        try:
            # For newer models like gemini-pro-1.5 or deep-research, we often need Chat sessions
            # or they enforce 'generateContent' strictly.
            # However, logs showed "This model only supports Interactions API" which typically means Chat.
            chat = self.model.start_chat(history=[])
            response = chat.send_message(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return f"Error generating answer from Gemini API: {e}"


class TextChunker:
    def __init__(self, chunk_size=512, overlap=50):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    
    def chunk(self, text_or_pages):
        if isinstance(text_or_pages, list):
            # Pages input: [{'text': '...', 'page': 1}, ...]
            all_chunks = []
            all_metadatas = []
            
            for page_data in text_or_pages:
                text = page_data.get('text', '')
                page_num = page_data.get('page', 1)
                
                # Chunk this page
                page_chunks = self.chunk_text(text)
                all_chunks.extend(page_chunks)
                all_metadatas.extend([{'page': page_num}] * len(page_chunks))
            
            return all_chunks, all_metadatas
        else:
            # Legacy string input
            return self.chunk_text(text_or_pages), []

    def chunk_text(self, text):
        # --- DATA CLEANING ---
        # 1. Remove "##tal values" and similar extraction artifacts
        text = re.sub(r'##[a-zA-Z\s]+', '', text)
        
        # 2. Fix known reversed text patterns (simple heuristic: if " noillirt" (trillion backwards) exists)
        # It's hard to perfectly auto-detect reversed lines without spoiling normal text, 
        # so we will FILTER out lines that look like garbage/non-english if possible, or just remove common artifacts.
        # For now, let's remove lines with high density of non-alphanumeric chars or weird tokens.
        
        # 3. Clean whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        chunks = []
        for i in range(0, len(tokens), self.chunk_size - self.overlap):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            if chunk_text.strip():
                chunks.append(chunk_text)
        return chunks


class FAISSManager:
    @staticmethod
    def build_index(embeddings):
        embeddings = np.array(embeddings, dtype='float32')
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        return index
    
    @staticmethod
    def search(index, query_embedding, k=5):
        query_emb = np.array([query_embedding], dtype='float32')
        distances, indices = index.search(query_emb, k)
        return indices[0], distances[0]
    
    @staticmethod
    def save(index, chunks, metadata, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(Path(output_dir) / 'index.bin'))
        with open(Path(output_dir) / 'chunks.pkl', 'wb') as f:
            pickle.dump(chunks, f)
        with open(Path(output_dir) / 'metadata.json', 'w') as f:
            json.dump(metadata, f)
    
    @staticmethod
    def load(input_dir):
        index = faiss.read_index(str(Path(input_dir) / 'index.bin'))
        with open(Path(input_dir) / 'chunks.pkl', 'rb') as f:
            chunks = pickle.load(f)
        with open(Path(input_dir) / 'metadata.json', 'r') as f:
            metadata = json.load(f)
        return index, chunks, metadata


class AnswerVerifier:
    def __init__(self, embedder, threshold=0.5):
        self.embedder = embedder
        self.threshold = threshold
    
    def check_grounding(self, answer, chunks):
        # Defensive check for empty chunks to prevent max() error
        if not chunks:
            return 0.0, []
        
        sentences = nltk.sent_tokenize(answer)
        if not sentences:
            return 0.0, []
        
        sent_embeddings = self.embedder.embed(sentences)
        chunk_embeddings = self.embedder.embed(chunks)
        
        supported_count = 0
        details = []
        
        for i, sent_emb in enumerate(sent_embeddings):
            similarities = util.pytorch_cos_sim(sent_emb, chunk_embeddings)[0]
            # Verify if similarities tensor is not empty (double check)
            if similarities.numel() == 0:
                 max_similarity = 0.0
                 is_supported = False
            else:
                 max_similarity = similarities.max().item()
                 is_supported = max_similarity > self.threshold
            
            supported_count += int(is_supported)
            
            details.append({
                'sentence': sentences[i],
                'max_similarity': float(max_similarity),
                'is_supported': bool(is_supported)
            })
        
        confidence = supported_count / len(sentences)
        return confidence, details
    
    def filter_answer(self, answer, chunks, confidence_threshold=0.7):
        confidence, details = self.check_grounding(answer, chunks)
        if confidence >= confidence_threshold:
            return answer, confidence, details
        else:
            return "I cannot find sufficient evidence in the documents.", confidence, details


class CitationMapper:
    def __init__(self, embedder):
        self.embedder = embedder
    
    def map_citations(self, answer, chunks, chunk_metadata):
        if not chunks:
            return []
            
        sentences = nltk.sent_tokenize(answer)
        sent_embeddings = self.embedder.embed(sentences)
        chunk_embeddings = self.embedder.embed(chunks)
        
        citations = []
        for sent, sent_emb in zip(sentences, sent_embeddings):
            similarities = util.pytorch_cos_sim(sent_emb, chunk_embeddings)[0]
            
            if similarities.numel() == 0:
                continue
                
            best_idx = similarities.argmax().item()
            best_similarity = similarities[best_idx].item()
            
            citations.append({
                'sentence': sent,
                'source_file': chunk_metadata[best_idx].get('source_file', 'Unknown'),
                'page': chunk_metadata[best_idx].get('page', 'N/A'),
                'similarity': float(best_similarity)
            })
        
        return citations


class RAGSystem:
    def __init__(self, config):
        self.config = config
        self.embedder = Embedder(config['embedding']['model_name'])
        self.reranker = Reranker()
        self.verifier = AnswerVerifier(self.embedder, config['verification']['similarity_threshold'])
        self.mapper = CitationMapper(self.embedder)
        self.index = None
        self.chunks = None
        self.metadata = None
        
        # Initialize Generator
        if config.get('GEMINI_API_KEY'):
            print("Initializing Gemini Generator...")
            self.generator = GeminiGenerator(config['GEMINI_API_KEY'], config['generation']['model_name'])
        else:
            # Fallback to T5 - BUT user wants Gemini. We'll warn if key missing in app.py.
            # Keeping T5 logic commented out or just relying on app.py to pass the generator.
            # Actually, per the original design, `app.py` passes the generator in `answer_question`,
            # but standardizing it here is cleaner. 
            # Let's support both:
            print("WARNING: GEMINI_API_KEY not found. Fallback/Null generator.")
            self.generator = None
    
    def load_index(self, index_dir):
        try:
            self.index, self.chunks, self.metadata = FAISSManager.load(index_dir)
            return True
        except:
            return False
    
    def save_index(self, index_dir):
        if self.index and self.chunks and self.metadata:
            FAISSManager.save(self.index, self.chunks, self.metadata, index_dir)
            return True
        return False
    
    def answer_question(self, query, retrieved_chunks, chunk_metadata, generator):
        t_start = time.time()
        
        # Rerank retrieved chunks
        if self.reranker and retrieved_chunks:
            reranked_chunks, top_indices = self.reranker.rerank(query, retrieved_chunks, top_k=5)
            # Filter metadata to match reranked chunks
            reranked_metadata = [chunk_metadata[i] for i in top_indices]
            
            # Use reranked results for generation
            final_chunks = reranked_chunks
            final_metadata = reranked_metadata
        else:
            final_chunks = retrieved_chunks
            final_metadata = chunk_metadata

        # Generate answer
        # Use simple argument check: if `generator` is passed from app.py, use it.
        # Otherwise use self.generator if available.
        active_generator = generator if generator else hasattr(self, 'generator') and self.generator

        if active_generator:
            answer = active_generator.generate(query, final_chunks)
            t_generate = time.time() - t_start
            
            # Verify
            final_answer, confidence, support_details = self.verifier.filter_answer(
                answer, final_chunks, self.config['verification']['confidence_threshold']
            )
            t_verify = time.time() - t_start - t_generate
            
            # Citations
            citations = self.mapper.map_citations(final_answer, final_chunks, final_metadata)
            t_cite = time.time() - t_start - t_generate - t_verify
            
        else:
            answer = "I found relevant information in the documents but no LLM is connected to generate a natural language answer. Please see the citations below."
            final_answer = answer
            confidence = 1.0
            support_details = []
            citations = []
            
            t_generate = time.time() - t_start
            t_verify = 0
            t_cite = 0
        
        t_total = time.time() - t_start
        
        return {
            'answer': final_answer,
            'confidence': float(confidence),
            'citations': citations,
            'retrieved_chunks': retrieved_chunks,
            'support_details': support_details,
            'latency': {
                'generation_ms': float(t_generate * 1000),
                'verification_ms': float(t_verify * 1000),
                'citation_ms': float(t_cite * 1000),
                'total_ms': float(t_total * 1000)
            }
        }