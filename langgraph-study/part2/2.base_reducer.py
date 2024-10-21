from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    foo: int

def node_1(state):
    print("---Node 1---")
    return {"foo": state['foo'] + 1}

def node_2(state):
    print("---Node 2---")
    return {"foo": state['foo'] + 1}

def node_3(state):
    print("---Node 3---")
    return {"foo": state['foo'] + 1}

# Build graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_1", "node_3")
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Add
graph = builder.compile()

# 현재 이렇게 하면 node_2 와 node_3 이 동시에 가기 때문에 에러 발생
# output = graph.invoke({"foo" : 0})
# print(output)
#------------------------------------------------------------------------------------------------------------------------------------------------
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from operator import add
from typing import Annotated
class State(TypedDict):
    foo: Annotated[list[int] , add]

def node_1(state):
    print("---Node 1---")
    return {"foo": [state['foo'][0] + 1]}



# Build graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)


# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", END)

# Add
graph = builder.compile()

# output = graph.invoke({"foo" : [0]})
# print(output)

#---------------------------------------------------------------------------------------------------------------------------------
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from operator import add
from typing import Annotated
class State(TypedDict):
    foo: Annotated[list[int] , add]

def node_1(state):
    print("---Node 1---")
    return {"foo": [state['foo'][-1] + 1]}

def node_2(state):
    print("---Node 2---")
    return {"foo": [state['foo'][-1] + 1]}

def node_3(state):
    print("---Node 3---")
    return {"foo": [state['foo'][-1] + 1]}

# Build graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_1", "node_3")
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Add
graph = builder.compile()

output = graph.invoke({"foo" : [1]})
print(output)