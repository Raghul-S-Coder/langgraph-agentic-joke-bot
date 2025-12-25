import os
from _operator import add
from typing import Literal, List
from typing_extensions import Annotated
from pydantic import BaseModel
from pyjokes import get_joke
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_groq.chat_models import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.output_parsers import StrOutputParser

"""
    Joke bot:
        It will give the jokes from pyjoke and LLM based on the configuration.
        using langgraph
        
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


load_dotenv()
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model=os.getenv("GROQ_MODEL"),
    temperature=0.3
)
template = ChatPromptTemplate.from_template(
    """
    Your are a joke generator.
    
    Strict instruction:
    #### 
    1) you have to return only one joke always
    2) return only joke no more explanation or question. 
    3) Dont repeat the joke again
    4) always it should be programs joke
    
    You have generate joke in langauge: {ln}
    expected joke category: {category}

    previous history: 
    {history}
    """
)
llm_chain = template | llm | StrOutputParser()


class Joke(BaseModel):
    text: str
    category: str


class JokeState(BaseModel):
    # jokes: Annotated[List[Joke], add] = []
    jokes: List[Joke] = []
    jokes_choice: Literal["n", "c", "q", "r", "l", "t"] = "n"  # next joke, change category, or quit
    category: Literal["neutral", "chuck", "all"] = "neutral"
    language: Literal["cs", "de", "en", "es", "eu", "fr", "gl", "hu", "it", "lt", "pl", "ru", "sv"] = "en"
    joke_type: Literal["LLM", "PYJOKE"] = "PYJOKE"
    quit: bool = False


def show_menu(state: JokeState) -> dict:
    user_input = input("[n] Next  [c] Category  [q] Quit  [r] Reset Jokes  [l] Change language [t] change type\n> ").strip().lower()
    return {"jokes_choice": user_input}


def reset_jokes(state: JokeState) -> dict:
    print("clearing history....")
    return {
        "jokes": [],
        "language": "en",
        "category": "neutral",
        "joke_type": "PYJOKE"
    }


def change_type(state: JokeState) -> dict:
    types = ["LLM", "PYJOKE"]
    user_input = int(input("Choose one [0] LLM, [1] PYJOKE\n>").strip())
    print("changing too... ", types[user_input])
    return {
        "joke_type": types[user_input]
    }


def select_category(state: JokeState) -> dict:
    categories = ["neutral", "chuck", "all"]
    selection = int(input("Select category [0=neutral, 1=chuck, 2=all]: ").strip())
    return {"category": categories[selection]}


def fetch_joke(state: JokeState) -> dict:
    if state.joke_type == "LLM":
        history = ""
        value = len(state.jokes) - 5
        if value <= 0:
            value = len(state.jokes)
        for his in state.jokes[value:]:
            history += "\n" + his.text

        response = llm_chain.invoke({"category": state.category, "ln": state.language, "history": history})
        print("LLM Joke: ", response, " category ", state.category, " lg: ", state.language)
        joke = Joke(text=response, category=state.category)
        state.jokes.append(joke)
        return {
            "jokes": state.jokes
        }
    else:
        joke_text = get_joke(language=state.language, category=state.category)
        new_joke = Joke(text=joke_text, category=state.category)
        print(joke_text)
        state.jokes.append(new_joke)

        return {"jokes": state.jokes}


def change_language(state: JokeState) -> JokeState:
    languages = ["cs", "de", "en", "es", "eu", "fr", "gl", "hu", "it", "lt", "pl", "ru", "sv"]
    user_input = input("choose language: [cs], [de], [en], [es], "
                       "[eu], [fr], [gl], [hu], [it], [lt], [pl], [ru], [sv]\n>")
    state.language = user_input
    return state


def exit_bot(state: JokeState) -> dict:
    print("exiting....")
    return {"quit": True}


def route_choice(state: JokeState) -> str:
    if state.jokes_choice == "n":
        return "fetch_joke"
    elif state.jokes_choice == "c":
        return "select_category"
    elif state.jokes_choice == "q":
        return "exit_bot"
    elif state.jokes_choice == "r":
        return "reset_jokes"
    elif state.jokes_choice == "l":
        return "change_language"
    elif state.jokes_choice == "t":
        return "change_type"
    return "exit_bot"


workflow = StateGraph(JokeState)
workflow.add_node("show_menu", show_menu)
workflow.add_node("select_category", select_category)
workflow.add_node("exit_bot", exit_bot)
workflow.add_node("fetch_joke", fetch_joke)
workflow.add_node("reset_jokes", reset_jokes)
workflow.add_node("change_language", change_language)
workflow.add_node("change_type", change_type)

workflow.add_edge(START, "show_menu")
workflow.add_conditional_edges(
    "show_menu",
    route_choice,
    {
               "fetch_joke": "fetch_joke",
               "select_category": "select_category",
               "exit_bot": "exit_bot",
               "reset_jokes": "reset_jokes",
               "change_language": "change_language",
               "change_type": "change_type"
        }
    )

workflow.add_edge("fetch_joke", "show_menu")
workflow.add_edge("select_category", "show_menu")
workflow.add_edge("reset_jokes", "show_menu")
workflow.add_edge("change_language", "show_menu")
workflow.add_edge("change_type", "show_menu")
workflow.add_edge("exit_bot", END)

graph = workflow.compile()

result = graph.invoke(JokeState(), config={"recursion_limit": 100})
print("result: ", result)


