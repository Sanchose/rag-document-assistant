import chromadb
from sentence_transformers import SentenceTransformer

from src.chunker import Chunk

EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


class VectorStore:
    """ChromaDB wrapper with local multilingual embeddings."""

    def __init__(self, path: str = "chroma_db", collection: str = "documents"):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(
            name=collection, metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        embeddings = self.model.encode([c.text for c in chunks]).tolist()
        self.collection.upsert(
            ids=[c.id for c in chunks],
            documents=[c.text for c in chunks],
            embeddings=embeddings,
            metadatas=[{"source": c.source, "page": c.page} for c in chunks],
        )

    def search(self, query: str, k: int = 4) -> list[dict]:
        if self.collection.count() == 0:
            return []
        embedding = self.model.encode([query]).tolist()
        result = self.collection.query(
            query_embeddings=embedding,
            n_results=min(k, self.collection.count()),
        )
        hits = []
        for text, meta, dist in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        ):
            hits.append(
                {
                    "text": text,
                    "source": meta["source"],
                    "page": meta["page"],
                    "distance": dist,
                }
            )
        return hits

    def clear(self) -> None:
        name = self.collection.name
        self.client.delete_collection(name)
        self.collection = self.client.get_or_create_collection(
            name=name, metadata={"hnsw:space": "cosine"}
        )
