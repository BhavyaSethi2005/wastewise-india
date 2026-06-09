"""
rag/retriever.py
Loads FAISS index. Builds it first if it doesn't exist (needed for HF Spaces).
"""

from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

INDEX_DIR   = Path("faiss_index")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Build index if missing (first run on HF Spaces)
if not (INDEX_DIR / "index.faiss").exists():
    print("FAISS index not found — building now...")
    from rag.ingest import build_index
    build_index()
    print("FAISS index built successfully.")

_embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
_index = FAISS.load_local(str(INDEX_DIR), _embeddings, allow_dangerous_deserialization=True)


def retrieve(query: str, k: int = 3) -> str:
    docs = _index.similarity_search(query, k=k)
    return "\n---\n".join(d.page_content for d in docs)