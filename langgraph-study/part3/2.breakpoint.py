from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
    a: first int
    b: second int

    """
    return a * b

# This will be a tool
def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
    a: first int
    b: second int
    """
    return a + b

def divide(a: int, b: int) -> float:
    """Divides a and b.

    Args:
    a: first int
    b: second int
    """
    return a / b

tools = [add, multiply, divide]
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

# System message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# Node
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# Graph
builder = StateGraph(MessagesState)

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine how the control flow moves
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)

builder.add_edge("tools", "assistant")

memory = MemorySaver()
graph = builder.compile(interrupt_before=["tools"], checkpointer=memory)


#--------------------------------Step 1-------------------------------------------
# # Input
# initial_input = {"messages": "Multiply 2 and 3"}

# # Thread
# thread = {"configurable": {"thread_id": "1"}}

# # Run the graph until the first interruption
# for event in graph.stream(initial_input, thread, stream_mode="values"):
#     event['messages'][-1].pretty_print()

# state = graph.get_state(thread)
# print(state.next)


# for event in graph.stream(None, thread, stream_mode="values"):
#     event['messages'][-1].pretty_print()

#--------------------------------Step 2-------------------------------------------

# Input
initial_input = {"messages": "Multiply 2 and 3"}

# Thread
thread = {"configurable": {"thread_id": "2"}}

# Run the graph until the first interruption
for event in graph.stream(initial_input, thread, stream_mode="values"):
    event['messages'][-1].pretty_print()

# Get user feedback
user_approval = input("Do you want to call the tool? (yes/no): ")

# Check approval
if user_approval.lower() == "yes":
    # If approved, continue the graph execution
    for event in graph.stream(None, thread, stream_mode="values"):
        event['messages'][-1].pretty_print()
else:
    print("Operation cancelled by user.")

#--------------------------------Step 3-------------------------------------------

# from langgraph_sdk import get_client
# import asyncio

# async def stream_messages():
#     initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}
#     client = get_client(url="http://localhost:8080")
#     assistant_id = "agent"
#     thread = await client.threads.create()

#     async for chunk in client.runs.stream(
#         thread["thread_id"],
#         assistant_id,
#         input=initial_input,
#         stream_mode="values",
#         interrupt_before=["tools"],
#     ):
#         print(f"Receiving new event of type: {chunk.event}...")
#         messages = chunk.data.get('messages', [])
#         if messages:
#             print(messages[-1])
#         print("-" * 50)

# # 비동기 함수를 실행하려면 이벤트 루프에서 호출해야 함
# asyncio.run(stream_messages())

