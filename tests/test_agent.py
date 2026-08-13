from app.agents.agent import run_agent


def test_agent_routes_finance_concept():
    response = run_agent("What is free cash flow?")
    assert any("explain_finance_concept" in step for step in response.trace)
    assert "operations" in response.answer.lower()


def test_agent_handles_empty_query():
    response = run_agent(" ")
    assert "Please enter" in response.answer
