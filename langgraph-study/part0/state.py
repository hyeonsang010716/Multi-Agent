from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class MyState(TypedDict):
    counter: int
    result : int

graph = StateGraph(MyState)

def increment(state):
    return {"result": state["counter"] + 1}

graph.add_node("increment", increment)

graph.add_edge(START, "increment")

graph.add_edge("increment", END)

app = graph.compile()

result = app.invoke({"counter": 0})
print(result) # {'counter': 0, 'result': 1}