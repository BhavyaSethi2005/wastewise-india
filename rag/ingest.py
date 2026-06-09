"""
rag/ingest.py
Reads all .txt files from knowledge_base/ → chunks → embeds → saves FAISS index.
Run this ONCE: python -m rag.ingest
Re-run only if you add new items to knowledge_base/.
"""

from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

KB_DIR     = Path("knowledge_base")
INDEX_DIR  = Path("faiss_index")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def build_index():
    # 1. Load all .txt files
    docs = []
    for file in KB_DIR.glob("*.txt"):
        text = file.read_text(encoding="utf-8")
        docs.append(text)
        print(f"  Loaded: {file.name} ({len(text)} chars)")

    if not docs:
        raise FileNotFoundError(f"No .txt files found in {KB_DIR}/")

    # 2. Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    chunks = splitter.create_documents(docs)
    print(f"  Total chunks: {len(chunks)}")

    # 3. Embed + build FAISS index
    print("  Embedding... (takes ~1 min first time, model downloads automatically)")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    index = FAISS.from_documents(chunks, embeddings)

    # 4. Save to disk
    INDEX_DIR.mkdir(exist_ok=True)
    index.save_local(str(INDEX_DIR))
    print(f"  FAISS index saved to {INDEX_DIR}/")


if __name__ == "__main__":
    print("Building FAISS index from knowledge base...")
    build_index()
    print("Done.")