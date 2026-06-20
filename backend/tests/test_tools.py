"""P1 — tool registry tests (no network, no LLM)."""

from rudra.agents.tools import ToolContext, build_default_registry


async def test_calculator_exact():
    reg = build_default_registry(include_code=False)
    ctx = ToolContext()
    assert await reg.execute("calculator", {"expression": "2*(3+4)"}, ctx) == "14"
    assert await reg.execute("calculator", {"expression": "10/4"}, ctx) == "2.5"


async def test_calculator_rejects_code():
    reg = build_default_registry(include_code=False)
    out = await reg.execute("calculator", {"expression": "__import__('os').system('echo hi')"}, ToolContext())
    assert "could not evaluate" in out.lower()


async def test_current_time_returns_text():
    reg = build_default_registry(include_code=False)
    assert await reg.execute("current_time", {}, ToolContext())


async def test_unknown_tool_message():
    reg = build_default_registry(include_code=False)
    out = await reg.execute("does_not_exist", {}, ToolContext())
    assert "unknown tool" in out.lower()


async def test_search_memory_requires_db():
    reg = build_default_registry(include_code=False)
    out = await reg.execute("search_memory", {"query": "x"}, ToolContext(db=None))
    assert "database" in out.lower()


def test_registry_exposes_core_tools():
    names = set(build_default_registry(include_code=False).names())
    assert {"calculator", "current_time", "web_search", "search_memory", "use_skill"} <= names


def test_code_tool_added_only_when_enabled():
    assert "run_python" not in build_default_registry(include_code=False).names()
    assert "run_python" in build_default_registry(include_code=True).names()
