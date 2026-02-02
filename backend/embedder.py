import os
from typing import List, Tuple

import faiss
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Document,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore

from backend.file_loader import load_all_files

# --------------------
# Configuration
# --------------------

PERSIST_DIR = "vector_store"

EMBED_MODEL = HuggingFaceEmbedding(
    model_name="all-MiniLM-L6-v2",  # keep same model for now
    normalize=True
)

NODE_PARSER = SentenceSplitter(
    chunk_size=512,
    chunk_overlap=80,
)

# --------------------
# Index build / load
# --------------------

def build_or_load_index(data_dir: str = "data") -> VectorStoreIndex:
    """
    Build the vector index once, then load it on subsequent runs.
    """
    if os.path.exists(PERSIST_DIR):
        storage_context = StorageContext.from_defaults(
            persist_dir=PERSIST_DIR
        )
        index = load_index_from_storage(
            storage_context,
            embed_model=EMBED_MODEL,
        )
        print("✅ Loaded existing LlamaIndex")
        return index

    print("📄 Loading files...")
    files = load_all_files(data_dir)

    documents: List[Document] = []
    for filename, text in files:
        if not text.strip():
            continue

        documents.append(
            Document(
                text=text,
                metadata={"source": filename},
            )
        )

    print(f"📦 Loaded {len(documents)} documents")

    DIMENSION = 384  # all-MiniLM-L6-v2
    faiss_index = faiss.IndexFlatIP(DIMENSION)

    vector_store = FaissVectorStore(faiss_index)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    index = VectorStoreIndex.from_documents(
        documents,
        embed_model=EMBED_MODEL,
        storage_context=storage_context,
        transformations=[NODE_PARSER],
    )

    index.storage_context.persist(PERSIST_DIR)
    print("✅ Index built and persisted")

    return index

# --------------------
# Search (drop-in replacement)
# --------------------

_index: VectorStoreIndex | None = None

def search(query: str, top_k: int = 6) -> List[Tuple[str, str]]:
    """
    Drop-in replacement for your old `search()` function.
    Returns: [(chunk_text, source_file), ...]
    """
    global _index

    if _index is None:
        _index = build_or_load_index()

    query_engine = _index.as_retriever(
        similarity_top_k=top_k
    )

    nodes = query_engine.retrieve(query)

    results = []
    for node in nodes:
        text = node.node.text
        source = node.node.metadata.get("source", "unknown")
        results.append((text, source))

    return results
