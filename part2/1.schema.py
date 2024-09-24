from typing import TypedDict
from typing import Literal
from langgraph.graph import StateGraph, START, END
import random


# 스키마 구현
class TypeDictState(TypedDict):
    name: str
    mode: Literal["happy", "sad"]


def node_1(state):
    print("---Node 1---")
    return {"name": state["name"] + " is..."}


def node_2(state):
    print("---Node 2---")
    return {"mode": "happy"}


def node_3(state):
    print("---Node 3---")
    return {"mode": "sad"}


def decide_mode(state) -> Literal["node_2", "node_3"]:
    if random.random() < 0.5:
        return "node_2"
    return "node_3"


# Build graph
builder = StateGraph(TypeDictState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic
builder.add_edge(START, "node_1")
builder.add_conditional_edges("node_1", decide_mode)
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Add
graph = builder.compile()

# print(graph.invoke({"name" : "hyeonsang"}))  # 여기서 알 수 있는 사실은 노드를 지날수록 return 값이 key에 들어간다.
# print(graph.invoke(TypeDictState(name = "Hyeonsang" , mode="sad"))) #여기서 알 수 있는 사실은 return 값이 이미 있는 경우에는 바뀐다.

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 잘못된 입력이 왔을 경우 에러를 발생시키는 스키마
from langchain_core.pydantic_v1 import BaseModel, validator, ValidationError


class PydanticState(BaseModel):
    name: str
    mode: Literal["happy", "sad"]

    @validator("mode")
    def validate_mode(cls, value):
        if value not in ["happy", "sad"]:
            raise ValidationError("Each mode must be either 'happy' or 'sad'")
        return value


try:
    state = PydanticState(name="hyeonsang", mode="hahaha")
except ValidationError as e:
    print("Validation Error:", e)
