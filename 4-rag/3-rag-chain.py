"""Step 3: RAG as a chain - retrieve the relevant chunks, then let the model answer.

Run: uv run python 4-rag/3-rag-chain.py
"""

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable, RunnableLambda, RunnablePassthrough

from learning_langchain.cli import ask
from learning_langchain.models import get_chat_model, get_embeddings
from learning_langchain.rag import (
    build_vector_store,
    format_documents,
    load_markdown_documents,
    split_documents,
)

# Load environment variables (API keys, LLM_PROVIDER, ...) from the .env file.
load_dotenv()

# The model must answer ONLY from the retrieved context - like an open-book
# exam where the student may only quote the pages handed to them.
RAG_PROMPT = ChatPromptTemplate(
    [
        (
            "system",
            "You answer questions about operational runbooks. Use ONLY the context below. "
            "If the answer is not in the context, say you don't know. Cite the source file.\n\n"
            "Context:\n{context}",
        ),
        ("user", "{question}"),
    ]
)


def build_rag_chain(retriever: BaseRetriever, model: BaseChatModel) -> Runnable:
    """The input (a question string) flows into two branches:
    - context: retriever finds the chunks, format_documents joins them
    - question: RunnablePassthrough keeps the question as-is
    Then prompt -> model -> StrOutputParser produce the final text."""
    return (
        {"context": retriever | RunnableLambda(format_documents), "question": RunnablePassthrough()}
        | RAG_PROMPT
        | model
        | StrOutputParser()
    )


def main() -> None:
    chunks = split_documents(load_markdown_documents())
    # as_retriever() wraps the vector store in the standard Retriever
    # interface (a Runnable: string in, list of Documents out).
    retriever = build_vector_store(chunks, get_embeddings()).as_retriever(search_kwargs={"k": 3})

    model = get_chat_model(
        fake_responses=[
            "(fake) Roll back if a deploy happened in the last hour; otherwise scale to 6 replicas."
        ]
    )
    question = ask("Ask about the runbooks", "checkout-api has high CPU. What should I do?")
    print("\nAnswer:", build_rag_chain(retriever, model).invoke(question))


if __name__ == "__main__":
    main()
