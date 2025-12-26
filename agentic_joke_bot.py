# from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from typing import Literal

from main_v1 import (
    JokeState,
    select_category,
    exit_bot,
    reset_jokes,
    change_language,
    change_type
)

"""
    Agentic Joke bot:
        It will give the jokes from pyjoke and LLM based on the configuration.
        It have joke writer and critic [which is used to evaluate the joke] with some limited iteration
        using langgraph
        
    Critic: 
        LLM based and Human in loop evaluation based on the configuration

    Configurations:
        joke_type -> pyjoke or llm
        language -> it supports multiple language support
        category -> neutral, chuck, all

    options:
        fetch_joke -> to get the joke
        select_category -> to change the category
        reset_joke -> to clear the history
        change_language -> to change the joke language
        change_type -> choose llm or pyjoke 
        show_menu -> to show above options to get inside
        exit_bot -> to stop
"""


class AgenticBotState(JokeState):
    retry_count: int = 3
    critic_type: Literal["LLM", "HUMAN"] = "HUMAN"
    return_response: Literal[True, False] = False


def show_agentic_menu(state: AgenticBotState) -> dict:
    user_input = input("[n] Next  [c] Category  [q] Quit  [r] Reset Jokes  "
                       "[l] Change language  [t] change type  [cc] change critic\n> ").strip().lower()
    return {"jokes_choice": user_input}


def change_agentic_critic(state: AgenticBotState) -> dict:
    user_input = int(input("choose one to change critic type: [0] LLM  [1] HUMAN\n>").strip())
    critic_types = ["LLM", "HUMAN"]
    return {
        "critic_type": critic_types[user_input]
    }


def llm_agentic_joke():
    pass


def agentic_pyjoke():
    pass


def llm_agentic_critic():
    pass


def human_agentic_critic():
    pass


def router(state: AgenticBotState) -> str:
    if state.jokes_choice == "n":
        return ""


def check_critic_condition(state: AgenticBotState) -> str:
    return ""


def check_joke_type(state: AgenticBotState) -> str:
    return state.joke_type


def prepare_graph():
    graph = StateGraph(AgenticBotState)

    graph.add_node("show_menu", show_agentic_menu)
    graph.add_node("select_category", select_category)
    graph.add_node("exit_bot", exit_bot)
    graph.add_node("llm_fetch_joke", llm_agentic_joke)
    graph.add_node("pyjoke", agentic_pyjoke)
    graph.add_node("reset_jokes", reset_jokes)
    graph.add_node("change_language", change_language)
    graph.add_node("change_type", change_type)
    graph.add_node("change_critic", change_agentic_critic)
    graph.add_node("llm_critic", llm_agentic_critic)
    graph.add_node("human_critic", human_agentic_critic)

    graph.add_edge(START, "show_menu")
    graph.add_conditional_edges(
        "show_menu",
        router,
        {
            "LLM": "llm_fetch_joke",
            "PYJOKE": "pyjoke",


            "reset_jokes": "reset_jokes",
            "change_type": "change_type",  # LLM or pyjoke
            "change_language": "change_language",
            "change_critic": "change_critic",
            "select_category": "select_category",
            "exit_bot": "exit_bot"
        }
    )
    graph.add_edge("reset_jokes", "show_menu")
    graph.add_edge("change_type", "show_menu")
    graph.add_edge("change_language", "show_menu")
    graph.add_edge("change_critic", "show_menu")
    graph.add_edge("select_category", "show_menu")
    graph.add_edge("change_critic", "show_menu")
    graph.add_edge("change_critic", "show_menu")

    graph.add_conditional_edges(
        "llm_fetch_joke",
        check_critic_condition,
        {
            "LLM": "llm_critic",
            "HUMAN": "human_critic",
            "show_menu": "show_menu"
        }
    )
    graph.add_conditional_edges(
        "pyjoke",
        check_critic_condition,
        {
            "LLM": "llm_critic",
            "HUMAN": "human_critic",
            "show_menu": "show_menu"
        }
    )
    graph.add_conditional_edges(
        "llm_critic",
        check_joke_type,
        {
            "LLM": "llm_fetch_joke",
            "PYJOKE": "pyjoke"
        }
    )
    graph.add_conditional_edges(
        "human_critic",
        check_joke_type,
        {
            "LLM": "llm_fetch_joke",
            "PYJOKE": "pyjoke"
        }
    )

    graph.add_edge("exit_bot", END)
    workflow = graph.compile()

    # display(Image(workflow.get_graph().draw_mermaid_png()))
