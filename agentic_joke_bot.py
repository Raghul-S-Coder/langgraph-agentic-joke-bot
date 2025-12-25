
from langgraph.graph import StateGraph
from main_v1 import (
    show_menu,
    JokeState
)


class AgenticBotState(JokeState):
    retry_count: int = 3


def prepare_graph():
    graph = StateGraph(AgenticBotState)

    graph.add_node("show_manu", show_menu)
    # graph.add_node("", )
