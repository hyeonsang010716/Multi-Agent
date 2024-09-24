from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from operator import add
from typing import Annotated
#None 타입이 들어올 경우 빈 리스트로 바꿔주도록 변경
def reduce_list(left: list | None, right: list | None) -> list:
    """
    Safely combine two lists, handling cases where either or both inputs might be None.

    Args:
        left (list | None): The first list to combine, or None.
        right (list | None): The second list to combine, or None.

    Returns:
        list: A new list containing all elements from both input lists.
              If an input is None, it's treated as an empty list.
    """
    if not left:
        left = []
    if not right:
        right = []
    return left + right

# class DefaultState(TypedDict):
#     foo: Annotated[list[int], add]

class CustomReducerState(TypedDict):
    foo: Annotated[list[int], reduce_list]

def node_1(state):
    print("---Node 1---")
    return {"foo": [2]}

# Build graph
builder = StateGraph(CustomReducerState)
builder.add_node("node_1", node_1)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

# Add
graph = builder.compile()

# try:
#     print(graph.invoke({"foo": None}))
# except TypeError as e:
#     print(f"TypeError occurred: {e}")

#----------------------------------------------------------------------------------------------------------

from typing import Annotated
from langgraph.graph import MessagesState
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

# Define a custom TypedDict that includes a list of messages with add_messages reducer
class CustomMessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    added_key_1: str
    added_key_2: str
    # etc

# Use MessagesState, which includes the messages key with add_messages reducer
class ExtendedMessagesState(MessagesState):
    # Add any keys needed beyond messages, which is pre-built
    added_key_1: str
    added_key_2: str
    # etc

from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage

# Initial state
initial_messages = [
    AIMessage(content="Hello! How can I assist you?", name="Model" , id = 1),
    HumanMessage(content="I'm looking for information on marine biology.", name="Lance" , id = 2)
]

# New message to add
new_message = AIMessage(content="Sure, I can help with that. What specifically are you interested in?", name="Model" , id = 2)

# Test
test = add_messages(initial_messages, new_message)

print("test :" , test)
print()
from langchain_core.messages import RemoveMessage

# Message list
messages = [AIMessage("Hi.", name="Bot", id=1)]
messages.append(HumanMessage("Hi.", name="Lance", id=2))
messages.append(AIMessage("So you said you were researching ocean mammals?", name="Bot", id=1))
messages.append(HumanMessage("Yes, I know about whales. But what others should I learn about?", name="Lance", id=4))

print("messages :" , messages)
print()

# Delete all but the 2 most recent messages
delete_messages = [RemoveMessage(id=m.id) for m in messages[:-2]]
print("delete_messages :" , delete_messages)
print()

current_messages = add_messages(messages, delete_messages)

print("current_messages :" , current_messages)
print()