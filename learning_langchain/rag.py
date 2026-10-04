"""Reusable RAG building blocks, taught step by step in 4-rag/1 and 4-rag/2."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

# The sample knowledge base: fictional runbooks shipped with the 4-rag module.
RUNBOOKS_DIR = Path(__file__).resolve().parent.parent / "4-rag" / "data" / "runbooks"


def load_markdown_documents(directory: Path = RUNBOOKS_DIR) -> list[Document]:
    """Read every .md file in `directory` into a Document, keeping the file
    path in metadata["source"] so answers can cite where they came from."""
    return [
        Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": str(path.name)})
        for path in sorted(directory.glob("*.md"))
    ]


def split_documents(
    documents: list[Document], chunk_size: int = 500, chunk_overlap: int = 50
) -> list[Document]:
    """Cut documents into overlapping chunks. add_start_index=True stores each
    chunk's character offset in metadata["start_index"]."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True
    )
    return splitter.split_documents(documents)


def build_vector_store(chunks: list[Document], embeddings: Embeddings) -> InMemoryVectorStore:
    """Embed every chunk and keep the vectors in memory (lost on exit)."""
    vector_store = InMemoryVectorStore(embedding=embeddings)
    vector_store.add_documents(chunks)
    return vector_store


def format_documents(documents: list[Document]) -> str:
    """Join retrieved chunks into one string for the prompt, with their source."""
    return "\n\n".join(
        f"[source: {doc.metadata.get('source', '?')}]\n{doc.page_content}" for doc in documents
    )
