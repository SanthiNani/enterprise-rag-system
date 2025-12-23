import pdfplumber
import os

pdf_files = [
    "data/raw/Generative AI, CS, Ethics Book.pdf",
    "data/raw/ML Engineer Guide.pdf",
    "data/raw/RAG Paper.pdf"
]

base_dir = os.path.dirname(os.path.abspath(__file__))

print("--- PDF CONTENT EXTRACT ---")

with open("extracted_content.txt", "w", encoding="utf-8") as f:
    for pdf_file in pdf_files:
        path = os.path.join(base_dir, pdf_file)
        f.write(f"\n{'='*20}\nFILE: {pdf_file}\n{'='*20}\n")
        try:
            with pdfplumber.open(path) as pdf:
                # Extract text from pages 1-3 (skip cover usually)
                text = ""
                for i in range(min(3, len(pdf.pages))):
                    text += pdf.pages[i].extract_text() or ""
                f.write(text)
        except Exception as e:
            f.write(f"Error: {e}")
