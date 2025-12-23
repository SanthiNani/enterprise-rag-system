import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import logging

logger = logging.getLogger(__name__)

class Generator:
    def __init__(self, model_name="google/flan-t5-small"):
        self.model_name = model_name
        self.pipeline = None
        self._initialize_model()

    def _initialize_model(self):
        try:
            logger.info(f"Loading generator model: {self.model_name}")
            # Use pipeline for easy inference
            # text2text-generation is suitable for T5 models
            self.pipeline = pipeline(
                "text2text-generation",
                model=self.model_name,
                device=-1, # Force CPU to avoid CUDA errors if GPU not present/configured
                model_kwargs={"low_cpu_mem_usage": True}
            )
            logger.info("Generator model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load generator model: {str(e)}")
            self.pipeline = None

    def generate(self, query, retrieved_chunks):
        if not self.pipeline:
            return "Error: Generator model not loaded."

        # Truncate chunks if too long (simple char count heuristic approx 4 chars per token)
        # Model limit is 512 tokens ~ 2000 chars. 
        # Reserve 200 chars for query + prompt
        max_context_length = 2000
        
        context = "\n".join(retrieved_chunks)
        if len(context) > max_context_length:
             context = context[:max_context_length] + "..."
             
        prompt = f"Answer the question based on the context below.\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"

        try:
            # Generate
            output = self.pipeline(
                prompt,
                max_length=200,
                truncation=True, # Explicitly enable truncation
                do_sample=False,
            )
            return output[0]['generated_text']
        except Exception as e:
            logger.error(f"Error during generation: {str(e)}")
            return "Error generating answer."
