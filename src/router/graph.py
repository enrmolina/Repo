import os
from typing import Annotated, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from .prompts import (
    POSTVENTA_PROMPT,
    PREVENTA_PROMPT,
    ROUTER_PROMPT,
    GENERICA_PROMPT,
    generica_response,
    postventa_response,
    preventa_response,
)
from .tools import fallback_route

load_dotenv()


class Decision(BaseModel):
    ruta: Literal["preventa", "postventa", "generica"] = Field(
        description="A qué agente va el mensaje."
    )
    motivo: str = Field(description="Una frase: por qué esa ruta.")


class RouterState(TypedDict, total=False):
    mensaje: str
    ruta: str
    motivo: str
    respuesta: str
    messages: Annotated[list[BaseMessage], add_messages]


def _model() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=os.getenv("MODELO", "gemini-3.5-flash-lite"),
    )


def router_node(state: RouterState) -> dict[str, str]:
    message = state["mensaje"]
    if os.getenv("GOOGLE_API_KEY"):
        decision = _model().with_structured_output(Decision).invoke(
            [SystemMessage(content=ROUTER_PROMPT), HumanMessage(content=message)]
        )
    else:
        route, reason = fallback_route(message)
        decision = Decision(ruta=route, motivo=reason)
    return {"ruta": decision.ruta, "motivo": decision.motivo}


def agente_preventa_node(state: RouterState) -> dict[str, str]:
    _ = PREVENTA_PROMPT
    return {"respuesta": preventa_response(state["mensaje"])}


def agente_postventa_node(state: RouterState) -> dict[str, str]:
    _ = POSTVENTA_PROMPT
    return {"respuesta": postventa_response(state["mensaje"])}


def respuesta_generica_node(state: RouterState) -> dict[str, str]:
    _ = GENERICA_PROMPT
    return {"respuesta": generica_response()}


def route_after_router(state: RouterState) -> str:
    return {
        "preventa": "agente_preventa",
        "postventa": "agente_postventa",
        "generica": "respuesta_generica",
    }[state["ruta"]]


def build_graph():
    graph = StateGraph(RouterState)
    graph.add_node("router", router_node)
    graph.add_node("agente_preventa", agente_preventa_node)
    graph.add_node("agente_postventa", agente_postventa_node)
    graph.add_node("respuesta_generica", respuesta_generica_node)
    graph.add_edge(START, "router")
    graph.add_conditional_edges("router", route_after_router)
    graph.add_edge("agente_preventa", END)
    graph.add_edge("agente_postventa", END)
    graph.add_edge("respuesta_generica", END)
    return graph.compile(checkpointer=MemorySaver())


GRAPH = build_graph()


def run_router(message: str, thread_id: str = "default") -> RouterState:
    return GRAPH.invoke(
        {"mensaje": message, "messages": [HumanMessage(content=message)]},
        {"configurable": {"thread_id": thread_id}},
    )
