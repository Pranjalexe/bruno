import pytest
from unittest.mock import patch
from langchain_core.documents import Document
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from bruno.rag.store import BrunoVectorStore

class DummyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        return [[1.0, 1.0] if "Python" in text else [1.0, 0.0] for text in input]

@pytest.fixture(autouse=True)
def mock_embedding_fn():
    with patch("bruno.rag.store.get_chroma_embedding_function", return_value=DummyEmbeddingFunction()):
        yield

def test_store_init(temp_data_dir):
    store = BrunoVectorStore(temp_data_dir)
    assert store.data_dir == temp_data_dir

def test_add_and_query_documents(temp_data_dir):
    store = BrunoVectorStore(temp_data_dir)
    docs = [
        Document(page_content="The quick brown fox jumps over the lazy dog.", metadata={"source": "test1.txt"}),
        Document(page_content="Python is a programming language.", metadata={"source": "test2.py"})
    ]
    
    store.add_documents(docs)
    
    # Simple query
    results = store.query("Python", n_results=1)
    assert len(results) == 1
    assert "Python" in results[0].page_content
    
def test_collections(temp_data_dir):
    store = BrunoVectorStore(temp_data_dir)
    store.add_documents([Document(page_content="test", metadata={"source": "test"})], collection_name="test_col")
    
    collections = store.list_collections()
    assert "test_col" in collections
    
    store.delete_collection("test_col")
    assert "test_col" not in store.list_collections()
