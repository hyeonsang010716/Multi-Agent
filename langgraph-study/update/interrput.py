# interrupt 와 Command를 사용한 바뀐 interrput 구조
# LangGraph 0.2.60 버전 필요


import uuid
from typing import TypedDict, Optional

from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


class State(TypedDict):
    """The graph state."""

    foo: str
    human_value: Optional[str]
    """Human value will be updated using an interrupt."""


def node(state: State):
    answer = interrupt(
        # This value will be sent to the client
        # as part of the interrupt information.
        "what is your age?"
    )
    print(f"> Received an input from the interrupt: {answer}")
    return {"human_value": answer}


builder = StateGraph(State)
builder.add_node("node", node)
builder.add_edge(START, "node")

# A checkpointer must be enabled for interrupts to work!
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {
    "configurable": {
        "thread_id": uuid.uuid4(),
    }
}

for chunk in graph.stream({"foo": "abc"}, config):
    print(chunk)


# Interrupt the graph execution.
# command = Command(resume="some input from a human!!!")

for chunk in graph.stream(Command(resume="some input from a human!!!"), config):
    print(chunk)