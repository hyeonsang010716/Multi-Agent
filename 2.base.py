from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o")


def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


llm_with_tools = llm.bind_tools([multiply])

# ---------------------------------------------TEST------------------------------------------------
tool_call = llm_with_tools.invoke(
    [HumanMessage(content=f"What is 2 multipled by 3", name="hyeonsang")]
)
# print(tool_call.additional_kwargs["tool_calls"])
# -------------------------------------------------------------------------------------------------

from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    pass


# ---------------------------------------------TEST------------------------------------------------
initial_messages = [
    AIMessage(content="Hello! How can I assist you?", name="Model"),
    HumanMessage(
        content="I'm looking for information on marine biology", name="Hyeonsang"
    ),
]
new_mesaage = AIMessage(
    content="Sure , I can help with that. What specifically are you interested in?",
    name="Model",
)

print(add_messages(initial_messages, new_mesaage))
# -------------------------------------------------------------------------------------------------
from langgraph.graph import StateGraph, START, END


# Node
def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("tool_calling_llm", tool_calling_llm)
builder.add_edge(START, "tool_calling_llm")
builder.add_edge("tool_calling_llm", END)
graph = builder.compile()

# print(graph.invoke({"messages": HumanMessage(content = "Hello!")}))
print(graph.invoke({"messages": HumanMessage(content="What is 2 multipled by 3")}))
