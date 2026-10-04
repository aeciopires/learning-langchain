"""Step 2 of RAG: turn chunks into vectors (embeddings) and search by meaning.

Run: uv run python 4-rag/2-embeddings-and-vector-store.py
"""

from dotenv import load_dotenv
from langchain_core.vectorstores import InMemoryVectorStore

from learning_langchain.config import is_fake_provider
from learning_langchain.models import get_embeddings
from learning_langchain.rag import load_markdown_documents, split_documents

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()


def main() -> None:
    # An embedding model turns text into a list of numbers (a vector). Texts
    # with similar meaning get vectors that point in similar directions -
    # like GPS coordinates, where nearby points are nearby places.
    embeddings = get_embeddings()
    vector = embeddings.embed_query("disk is full")
    first_numbers = [round(float(number), 4) for number in vector[:3]]
    print(f"'disk is full' -> vector with {len(vector)} numbers, first 3: {first_numbers}")

    # The vector store keeps every chunk next to its vector and finds the
    # closest ones to a question's vector (cosine similarity, for InMemoryVectorStore).
    chunks = split_documents(load_markdown_documents())
    vector_store = InMemoryVectorStore(embedding=embeddings)
    ids = vector_store.add_documents(chunks)
    print(f"Indexed {len(ids)} chunks.")

    if is_fake_provider():
        print("NOTE: fake embeddings are random-like - the results below are NOT semantic.")

    question = "What should I do when the log server runs out of disk space?"
    print(f"\nQuestion: {question}")
    for doc, score in vector_store.similarity_search_with_score(question, k=2):
        first_line = doc.page_content.splitlines()[0]
        print(f"  score={score:.3f} source={doc.metadata['source']} -> {first_line}")


if __name__ == "__main__":
    main()
