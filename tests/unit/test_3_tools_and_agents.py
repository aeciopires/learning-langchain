"""Tests for the 3-tools-and-agents module: tools are plain functions, and
agents are tested with a fake model that scripts the tool calls."""

from langchain_core.messages import AIMessage, ToolMessage

from learning_langchain.models import build_fake_chat_model
from tests._helpers import load_script


def test_tool_metadata_comes_from_the_function():
    script = load_script("3-tools-and-agents/1-first-tool.py")
    tool = script.check_disk_usage
    assert tool.name == "check_disk_usage"
    assert "disk space" in tool.description
    assert "path" in tool.args


def test_disk_usage_tool(tmp_path):
    script = load_script("3-tools-and-agents/1-first-tool.py")
    assert "GiB" in script.check_disk_usage.invoke({"path": str(tmp_path)})
    assert script.check_disk_usage.invoke({"path": str(tmp_path / "missing")}).startswith("Path not found")


def test_service_status_tool_handles_unknown_services():
    script = load_script("3-tools-and-agents/2-simple-agent.py")
    assert "status=degraded" in script.get_service_status.invoke({"service": "checkout-api"})
    assert script.get_service_status.invoke({"service": "nope"}).startswith("Unknown service")


def test_agent_runs_the_tool_the_model_asked_for():
    script = load_script("3-tools-and-agents/2-simple-agent.py")
    agent = script.build_agent(build_fake_chat_model(script.FAKE_RESPONSES))
    result = agent.invoke({"messages": [{"role": "user", "content": "anything unhealthy?"}]})

    tool_results = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert [m.name for m in tool_results] == ["list_services", "get_service_status"]
    assert "status=degraded" in tool_results[1].content
    assert isinstance(result["messages"][-1], AIMessage)
    assert "checkout-api is degraded" in result["messages"][-1].text


def test_memory_is_kept_per_thread():
    script = load_script("3-tools-and-agents/3-agent-with-memory.py")
    agent = script.build_agent(build_fake_chat_model(["a1", "a2", "a3"]))
    script.ask_agent(agent, "t1", "q1")
    script.ask_agent(agent, "t1", "q2")
    script.ask_agent(agent, "t2", "q3")

    thread_1 = agent.get_state({"configurable": {"thread_id": "t1"}}).values["messages"]
    thread_2 = agent.get_state({"configurable": {"thread_id": "t2"}}).values["messages"]
    assert [m.text for m in thread_1] == ["q1", "a1", "q2", "a2"]
    assert [m.text for m in thread_2] == ["q3", "a3"]


def test_review_tools_list_and_read_files(tmp_path):
    script = load_script("3-tools-and-agents/4-agent-review.py")
    (tmp_path / "app.py").write_text("print('hi')\n", encoding="utf-8")
    listing = script.list_python_files.invoke({"directory": str(tmp_path)})
    assert listing.endswith("app.py")
    assert script.read_file_content.invoke({"file_path": listing}) == "print('hi')\n"
    assert script.list_python_files.invoke({"directory": str(tmp_path / "x")}).startswith(
        "Directory not found"
    )
    assert script.read_file_content.invoke({"file_path": str(tmp_path / "x.py")}).startswith("File not found")


def test_review_temperature_parsing():
    script = load_script("3-tools-and-agents/4-agent-review.py")
    assert script.parse_temperature("0.7") == 0.7
    assert script.parse_temperature("hot") == script.DEFAULT_TEMPERATURE


def test_review_agent_main_runs_offline(no_stdin, capsys):
    load_script("3-tools-and-agents/4-agent-review.py").main()
    assert "(fake review)" in capsys.readouterr().out
