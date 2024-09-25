from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

#------------------------------------------------------------------------------ 두 개의 스키마
class OverallState(TypedDict):
    foo: int

class PrivateState(TypedDict):
    baz: int

def node_1(state: OverallState) -> PrivateState:
    print("---Node 1---")
    return {"baz": state['foo'] + 1}

def node_2(state: PrivateState) -> OverallState:
    print("---Node 2---")
    return {"foo": state['baz'] + 1}

# Build graph
builder = StateGraph(OverallState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", END)

# Add
graph = builder.compile()

output = graph.invoke({"foo" : 2})

# print(output)
#----------------------------------------------------------------------------- 기존

class OverallState(TypedDict):
    question: str
    answer: str
    notes: str

def thinking_node(state: OverallState):
    return {"answer": "bye", "notes": "... his name is Lance"}

def answer_node(state: OverallState):
    return {"answer": "bye Lance"}

graph = StateGraph(OverallState)
graph.add_node("answer_node", answer_node)
graph.add_node("thinking_node", thinking_node)

graph.add_edge(START, "thinking_node")
graph.add_edge("thinking_node", "answer_node")
graph.add_edge("answer_node", END)

graph = graph.compile()

output = graph.invoke({"question" : "hi"})

# print(output)

#----------------------------------------------------------------------------- 멀티 스키마
class InputState(TypedDict):
    question: str

class OutputState(TypedDict):
    answer: str

class OverallState(TypedDict):
    question: str
    answer: str
    notes: str

def thinking_node(state: InputState):
    return {"answer": "bye", "notes": "... his name is Lance"}

def answer_node(state: OverallState) -> OutputState:
    return {"answer": "bye Lance"}

graph = StateGraph(OverallState, input=InputState, output=OutputState) #여기서 input 과 output 스키마를 정의해준다.
graph.add_node("answer_node", answer_node)
graph.add_node("thinking_node", thinking_node)

graph.add_edge(START, "thinking_node")
graph.add_edge("thinking_node", "answer_node")
graph.add_edge("answer_node", END)

graph = graph.compile()

output = graph.invoke({"question" : "hi"})

print(output)
#output 스키마를 정의해줬기 때문에
# {'question': 'hi', 'answer': 'bye Lance', 'notes': '... his name is Lance'} -> {'answer': 'bye Lance'}
# answer만 출력되는 것을 볼 수 있다.