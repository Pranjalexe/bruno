"""
Embedding function factory.
"""
from chromadb.utils import embedding_functions
from langchain_core.embeddings import Embeddings

from bruno.config import get_settings


def get_embedding_function() -> Embeddings:
    """Returns LangChain Embeddings instance."""
    settings = get_settings()

    if settings.embedding_model.startswith("text-embedding-"):
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model=settings.embedding_model
        )
    else:
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name=settings.embedding_model)

def get_chroma_embedding_function() -> embedding_functions.EmbeddingFunction:
    """Returns ChromaDB EmbeddingFunction."""
    settings = get_settings()

    if settings.embedding_model.startswith("text-embedding-"):
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=settings.openai_api_key,
            model_name=settings.embedding_model
        )
    else:
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=settings.embedding_model
        )
