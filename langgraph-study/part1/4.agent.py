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

tools = [divide, add , multiply]

llm_with_tools = llm.bind_tools(tools)

from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage

sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

def assistant(state: MessagesState):
    return {
        "messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]
    }

from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode

# Graph
builder = StateGraph(MessagesState)

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
"assistant",
tools_condition,
)
builder.add_edge("tools", "assistant")
react_graph = builder.compile()

messages = [HumanMessage(content="Add 3 and 4. Multiply the output by 2. Divide the output by 5")]
messages = react_graph.invoke({"messages" : messages})

for m in messages['messages']:
    m.pretty_print()

#이전에는 END를 정의해줬지만, 이제는 tools_condition에서 도구를 호출하지 않으면 END로 가는 것으로 바뀜.