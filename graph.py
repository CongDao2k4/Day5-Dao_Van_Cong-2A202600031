from typing import Any

from langgraph.graph import START, StateGraph
from typing_extensions import TypedDict


class State(TypedDict):
    text: str


def node_a(state: State) -> dict[str, str]:
    return {"text": state["text"] + "a"}


def node_b(state: State) -> dict[str, str]:
    return {"text": state["text"] + "b"}


def build_app(checkpointer: Any = None):
    graph = StateGraph(State)
    graph.add_node("node_a", node_a)
    graph.add_node("node_b", node_b)
    graph.add_edge(START, "node_a")
    graph.add_edge("node_a", "node_b")
    if checkpointer is not None:
        return graph.compile(checkpointer=checkpointer)
    return graph.compile()
