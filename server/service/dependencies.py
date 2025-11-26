from functools import lru_cache

from langchain.chat_models import init_chat_model
from langchain_community.vectorstores import LanceDB
from langchain_openai import OpenAIEmbeddings
from langgraph.constants import END
from langgraph.graph import StateGraph
from tavily import TavilyClient

from server.model.AgentState import AgentState
from server.model.Predictor import Predictor
from server.service.workflow import predict_node, search_web_node, retrieve_internal_node, write_article, structure_node
import lancedb

OPENAI_MODEL_SMALL = "gpt-4o-mini"


@lru_cache
def get_llm():
    model = init_chat_model(OPENAI_MODEL_SMALL,
                            model_provider="openai",
                            temperature=0.8)

    return model


@lru_cache
def get_tavily():
    return TavilyClient()


@lru_cache
def get_predictor():
    return Predictor()


@lru_cache
def get_vector_store():
    db_path = "./resources/vector_store"

    db = lancedb.connect(db_path)

    table_name = "vectorstore"

    return LanceDB(
        connection=db,
        embedding=OpenAIEmbeddings(),
        table_name=table_name
    )


@lru_cache
def get_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("predict", predict_node)
    workflow.add_node("search", search_web_node)
    workflow.add_node("retrieve", retrieve_internal_node)
    workflow.add_node("write", write_article)
    workflow.add_node("structure", structure_node)

    workflow.set_entry_point("predict")
    workflow.add_edge("predict", "search")
    workflow.add_edge("search", "retrieve")
    workflow.add_edge("retrieve", "structure")
    workflow.add_edge("structure", "write")
    workflow.add_edge("write", END)

    graph = workflow.compile()

    return graph
