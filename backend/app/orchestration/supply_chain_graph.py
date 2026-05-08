from langgraph.graph import END, StateGraph

from app.agents.compliance_agent import compliance_agent_node
from app.agents.execution_agent import execution_agent_node
from app.agents.mitigation_strategist import mitigation_strategist_node
from app.agents.risk_analyst import risk_analyst_node
from app.orchestration.workflow_state import WorkflowState


def route_after_risk(
    state: WorkflowState,
) -> str:
    """
    Decide whether workflow should continue to mitigation.
    """

    if state.get("should_mitigate"):
        return "mitigation"

    return "end"


def route_after_mitigation(
    state: WorkflowState,
) -> str:
    """
    Decide whether workflow should continue to execution.
    """

    if state.get("should_execute"):
        return "execution"

    return "end"


def route_after_execution(
    state: WorkflowState,
) -> str:
    """
    Decide whether workflow should continue to compliance.
    """

    if state.get("should_audit"):
        return "compliance"

    return "end"


def build_supply_chain_graph():
    """
    Build the SupplyChain Guardian LangGraph workflow.
    """

    graph = StateGraph(WorkflowState)

    graph.add_node("risk_analyst", risk_analyst_node)
    graph.add_node("mitigation", mitigation_strategist_node)
    graph.add_node("execution", execution_agent_node)
    graph.add_node("compliance", compliance_agent_node)

    graph.set_entry_point("risk_analyst")

    graph.add_conditional_edges(
        "risk_analyst",
        route_after_risk,
        {
            "mitigation": "mitigation",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "mitigation",
        route_after_mitigation,
        {
            "execution": "execution",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "execution",
        route_after_execution,
        {
            "compliance": "compliance",
            "end": END,
        },
    )

    graph.add_edge("compliance", END)

    return graph.compile()


supply_chain_graph = build_supply_chain_graph()