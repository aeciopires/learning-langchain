"""Tests for the 4-rag module and learning_langchain/rag.py."""

from langchain_core.documents import Document
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda

from learning_langchain.models import build_fake_chat_model, get_embeddings
from learning_langchain.rag import (
    build_vector_store,
    format_documents,
    load_markdown_documents,
    split_documents,
)
from tests._helpers import echo_model, load_script


def test_runbooks_are_loaded_with_their_source():
    documents = load_markdown_documents()
    assert {doc.metadata["source"] for doc in documents} == {
        "certificate-expiry.md",
        "disk-full.md",
        "high-cpu.md",
    }


def test_chunks_respect_the_size_and_keep_the_offset():
    chunks = split_documents(load_markdown_documents(), chunk_size=200, chunk_overlap=20)
    assert all(len(chunk.page_content) <= 200 for chunk in chunks)
    assert all("start_index" in chunk.metadata and "source" in chunk.metadata for chunk in chunks)


def test_vector_store_finds_an_identical_text():
    # Fake embeddings are deterministic: the same text -> the same vector, so
    # searching for a chunk's exact text must return that chunk first.
    chunks = split_documents(load_markdown_documents())
    store = build_vector_store(chunks, get_embeddings())
    target = chunks[2]
    assert store.similarity_search(target.page_content, k=1)[0].page_content == target.page_content


def test_format_documents_cites_the_source():
    text = format_documents([Document(page_content="step 1", metadata={"source": "a.md"})])
    assert text == "[source: a.md]\nstep 1"


def test_rag_chain_puts_the_retrieved_context_in_the_prompt():
    script = load_script("4-rag/3-rag-chain.py")
    fixed_retriever = RunnableLambda(
        lambda question: [Document(page_content="scale to 6", metadata={"source": "x.md"})]
    )
    prompt_text = script.build_rag_chain(fixed_retriever, echo_model()).invoke("high cpu?")
    assert "[source: x.md]\nscale to 6" in prompt_text
    assert "Human: high cpu?" in prompt_text


def test_rag_agent_calls_the_search_tool():
    script = load_script("4-rag/4-rag-agent.py")
    store = build_vector_store(split_documents(load_markdown_documents()), get_embeddings())
    agent = script.build_agent(store, build_fake_chat_model(script.FAKE_RESPONSES))
    result = agent.invoke({"messages": [{"role": "user", "content": "cert expiring"}]})
    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert len(tool_messages) == 1
    assert "[source:" in tool_messages[0].content
