"""
Document ingestion pipeline.
"""
import concurrent.futures
import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml
from langchain_core.documents import Document
from langchain_text_splitters import (
    Language,
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from bruno.rag.store import BrunoVectorStore


@dataclass
class IngestResult:
    files_processed: int = 0
    chunks_created: int = 0
    files_skipped: int = 0
    errors: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

def chunk_log_file(log_text: str, source: str) -> list[Document]:
    # Try to split by common timestamp formats
    pattern = r'\n(?=\d{4}-\d{2}-\d{2}|\d{2}/\w{3}/\d{4}|\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})'
    entries = re.split(pattern, log_text)

    docs = []
    for i, entry in enumerate(entries):
        if entry.strip():
            # Truncate extremely long entries
            content = entry.strip()[:2000]
            docs.append(Document(
                page_content=content,
                metadata={"source": source, "chunk_index": i}
            ))
    return docs

def process_file(file_path: Path) -> list[Document]:
    """Process a single file and return chunked documents."""
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    ext = file_path.suffix.lower()
    source = str(file_path)

    if ext == ".md":
        headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
        md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        md_splits = md_splitter.split_text(text)

        char_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = char_splitter.split_documents(md_splits)
        for i, d in enumerate(docs):
            d.metadata["source"] = source
            d.metadata["chunk_index"] = i
        return docs

    elif ext == ".log":
        return chunk_log_file(text, source)

    elif ext == ".py":
        char_splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=500, chunk_overlap=50
        )
        docs = char_splitter.create_documents([text], metadatas=[{"source": source}])
        for i, d in enumerate(docs):
            d.metadata["chunk_index"] = i
        return docs

    elif ext in [".json", ".yaml", ".yml"]:
        try:
            if ext == ".json":
                data = json.loads(text)
                text = json.dumps(data, indent=2)
            else:
                data = yaml.safe_load(text)
                text = yaml.dump(data)
        except Exception:
            pass # fallback to plain text

        char_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = char_splitter.create_documents([text], metadatas=[{"source": source}])
        for i, d in enumerate(docs):
            d.metadata["chunk_index"] = i
        return docs

    else:
        # Default text splitting
        char_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = char_splitter.create_documents([text], metadatas=[{"source": source}])
        for i, d in enumerate(docs):
            d.metadata["chunk_index"] = i
        return docs

def ingest_path(path: Path | str, store: BrunoVectorStore, recursive: bool = False, collection: str = "knowledge_base") -> IngestResult:
    path = Path(path).resolve()
    result = IngestResult()

    if not path.exists():
        result.errors.append(f"Path does not exist: {path}")
        return result

    supported_exts = {".md", ".txt", ".log", ".py", ".rst", ".json", ".yaml", ".yml"}

    files_to_process = []
    if path.is_file():
        files_to_process.append(path)
    elif path.is_dir():
        pattern = "**/*" if recursive else "*"
        for f in path.glob(pattern):
            if f.is_file():
                if f.suffix.lower() in supported_exts:
                    files_to_process.append(f)
                else:
                    result.files_skipped += 1

    # Limit concurrency to 4 to prevent CPU/memory spikes on small machines
    max_workers = min(4, len(files_to_process) or 1)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(process_file, f): f for f in files_to_process}
        
        for future in concurrent.futures.as_completed(future_to_file):
            f = future_to_file[future]
            try:
                docs = future.result()
                if docs:
                    store.add_documents(docs, collection_name=collection)
                    result.files_processed += 1
                    result.chunks_created += len(docs)
                else:
                    result.files_skipped += 1
            except Exception as e:
                result.errors.append(f"Error processing {f}: {e}")

    return result
