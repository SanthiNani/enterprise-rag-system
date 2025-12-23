import pdfplumber
import os

pdf_file = "data/raw/RAG Paper.pdf"
base_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base_dir, pdf_file)

print(f"--- EXTRACTING: {pdf_file} ---")
try:
    with pdfplumber.open(path) as pdf:
        print(f"Pages: {len(pdf.pages)}")
        text = pdf.pages[0].extract_text()
        print(f"Page 1 Text:\n{text}")
except Exception as e:
    print(f"Error: {e}")
