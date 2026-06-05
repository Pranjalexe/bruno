"""
ChromaDB vector store wrapper.
"""
import hashlib
from datetime import datetime
from pathlib import Path

import chromadb
from langchain_core.documents import Document

from bruno.rag.embeddings import get_chroma_embedding_function


class BrunoVectorStore:
    def __init__(self, data_dir: Path | str):
        self.data_dir = Path(data_dir)
        self.client = chromadb.PersistentClient(path=str(self.data_dir))
        self.embedding_fn = get_chroma_embedding_function()

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(
            name=name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, docs: list[Document], collection_name: str = "knowledge_base"):
        if not docs:
            return

        collection = self.get_or_create_collection(collection_name)

        texts = []
        metadatas = []
        ids = []

        now = datetime.utcnow().isoformat()

        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "unknown")
            chunk_index = doc.metadata.get("chunk_index", i)
            file_type = Path(source).suffix.lstrip('.') if source != "unknown" else "txt"

            # Deterministic ID based on source and chunk
            doc_id = hashlib.md5(f"{source}:{chunk_index}".encode()).hexdigest()

            # Enhance metadata
            meta = doc.metadata.copy()
            meta["ingested_at"] = now
            meta["file_type"] = file_type
            meta["chunk_index"] = chunk_index

            texts.append(doc.page_content)
            metadatas.append(meta)
            ids.append(doc_id)

        # ChromaDB handles ignoring duplicates if we don't upsert, or we can use upsert
        collection.upsert(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query: str, collection_name: str = "knowledge_base", n_results: int = 5, filters: dict = None) -> list[Document]:
        collection = self.get_or_create_collection(collection_name)

        kwargs = {
            "query_texts": [query],
            "n_results": n_results
        }
        if filters:
            kwargs["where"] = filters

        results = collection.query(**kwargs)

        docs = []
        if results and results["documents"]:
            for i, text in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                docs.append(Document(page_content=text, metadata=meta))

        return docs

    def list_collections(self) -> list[str]:
        return [c.name for c in self.client.list_collections()]

    def delete_collection(self, name: str):
        try:
            self.client.delete_collection(name=name)
        except Exception:
            pass

    def get_stats(self) -> dict:
        stats = {}
        for name in self.list_collections():
            col = self.client.get_collection(name, embedding_function=self.embedding_fn)
            stats[name] = col.count()
        return stats
