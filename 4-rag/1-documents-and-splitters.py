"""Step 1 of RAG: load documents and split them into chunks. No model needed.

Run: uv run python 4-rag/1-documents-and-splitters.py
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from learning_langchain.rag import RUNBOOKS_DIR


def load_documents() -> list[Document]:
    """A Document is just text (page_content) plus a dict of metadata - like a
    library book (the text) with its catalog card (author, shelf, ...)."""
    return [
        Document(page_content=path.read_text(encoding="utf-8"), metadata={"source": path.name})
        for path in sorted(RUNBOOKS_DIR.glob("*.md"))
    ]


def split(documents: list[Document]) -> list[Document]:
    """RecursiveCharacterTextSplitter tries to cut on paragraphs first, then
    lines, then words, until each chunk fits chunk_size characters. The
    overlap repeats a bit of text between neighbors so an idea cut in half
    still appears whole in at least one chunk."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, add_start_index=True)
    return splitter.split_documents(documents)


def main() -> None:
    documents = load_documents()
    print(f"Loaded {len(documents)} documents from {RUNBOOKS_DIR}:")
    for doc in documents:
        print(f"  - {doc.metadata['source']}: {len(doc.page_content)} characters")

    chunks = split(documents)
    print(f"\nSplit into {len(chunks)} chunks. First chunk:")
    print(f"  metadata: {chunks[0].metadata}")
    print("  text:\n" + "\n".join(f"    {line}" for line in chunks[0].page_content.splitlines()))


if __name__ == "__main__":
    main()
