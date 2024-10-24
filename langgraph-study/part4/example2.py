# !pip install langchain-teddynote
#Tool init
from langchain_teddynote.tools.tavily import TavilySearch

tool = TavilySearch(max_results=3)

tools = [tool]

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")

llm_with_tools = llm.bind_tools(tools)


# State
class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    answer = llm_with_tools.invoke(state["messages"])
    return {"messages": [answer]}


from langgraph.graph import StateGraph

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

