"""
rag/retriever.py
Loads saved FAISS index and returns relevant chunks for a query.
"""

from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

INDEX_DIR   = Path("faiss_index")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Load once at module level
_embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
_index = FAISS.load_local(str(INDEX_DIR), _embeddings, allow_dangerous_deserialization=True)


def retrieve(query: str, k: int = 3) -> str:
    """
    Search FAISS index for query, return top-k chunks as single string.
    k=3 gives enough context without overloading the prompt.
    """
    docs = _index.similarity_search(query, k=k)
    return "\n---\n".join(d.page_content for d in docs)