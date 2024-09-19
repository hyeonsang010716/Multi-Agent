from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()

def multiply(a: int, b: int) -> int:
    """
    Multiplies two numbers.
    
    Args:
        a: first int
        b: second int
    
    Returns:
        A product of a and b.
    """
    return a * b

def add(a: int, b: int) -> int:
    """
    Adds two numbers.
    
    Args:
        a: first int
        b: second int
    
    Returns:
        Sum of a and b.
    """
    return a + b

def divide(a: int, b: int) -> float:
    """
    Divides two numbers.
    
    Args:
        a: first int
        b: second int
    
   Returns:
       Quotient of a divided by b.
   """
    return a / b

llm = ChatOpenAI(model="gpt-4o")

tools = [add , multiply , divide]

llm_with_tools = llm.bind_tools(tools)

