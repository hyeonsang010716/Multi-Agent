# add_conditional_edge -> Command
# LangGraph 0.2.60 버전 필요

from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing import TypedDict, List, Literal
import collections

# 그래프의 상태를 정의하는 클래스
class MyState(TypedDict):
    num_list: List[int]
    total: int
    avg: float
    avg_is: str

# StateGraph 인스턴스 생성
graph_builder = StateGraph(MyState)

# 노드 함수 정의
def list_sum(state: MyState):

    total = sum(state["num_list"])

    return {"total": total}

# Conditional Edge를 위한 Command 타입 반환
def list_avg(state: MyState) -> Command[Literal["print_integer", "print_not_integer"]]:

    avg = state["total"] / len(state["num_list"])

    if avg.is_integer():
        goto = "print_integer"
    else:
        goto = "print_not_integer"


    # return {"avg": avg}
    return Command(goto=goto, update={"avg": avg})


def print_integer(state: MyState):
    return {"avg_is": "Integer"}


def print_not_integer(state: MyState):
    return {"avg_is": "Not Integer"}


# 노드 추가
graph_builder.add_node("list_sum", list_sum)
graph_builder.add_node("list_avg", list_avg)
graph_builder.add_node("print_integer", print_integer)
graph_builder.add_node("print_not_integer", print_not_integer)

# 노드로 엣지 추가
graph_builder.add_edge(START, "list_sum")
graph_builder.add_edge("list_sum", "list_avg")

graph_builder.add_edge(["print_integer","print_not_integer"], END)


# 그래프 컴파일
graph = graph_builder.compile()
print(f"\n{graph}\n")
print(f"{isinstance(graph, Runnable)}\n")
print(f"{list(graph.channels.keys())}\n")


# 그래프 실행 - stream
events = graph.stream({"num_list": [1,2,3,4,5]}, stream_mode="values")
#events = graph.stream({"num_list": [1,2,3,4,5]}, stream_mode="updates")
#events = graph.stream({"num_list": [1,2,3,4,5]}, stream_mode="updates", output_keys="total") #output_keys : 스트림 할 State의 key 지정
#events = graph.stream({"num_list": [1,2,3,4,5]}, stream_mode="debug")

print(f"Type : {type(events)}\n")
print(f"Is Iterator? : {isinstance(events,collections.abc.Iterator)}\n")

for event in events:
    print(event)
    # for key, value in event.items():
    #     print(f"{key} : {value}")
    print("-"*50)







