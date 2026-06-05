"""
LangChain-compatible retriever wrapping BrunoVectorStore.
"""
from typing import Any

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field

from bruno.rag.store import BrunoVectorStore


class BrunoRetriever(BaseRetriever):
    store: BrunoVectorStore = Field(..., exclude=True)
    collection_name: str = "knowledge_base"
    k: int = 5
    filters: dict = None

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(self, query: str, *, run_manager: Any = None) -> list[Document]:
        return self.store.query(
            query=query,
            collection_name=self.collection_name,
            n_results=self.k,
            filters=self.filters
        )
