# API 키를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import OpenAI
# API 키 정보 로드
load_dotenv()

#init
class State(TypedDict):
    input: Annotated[list, add_messages]

llm = OpenAI(temperature=0)


def chatbot(state: State):
    return {"input": [llm.invoke(state["input"])]}


# Graph
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

graph_builder.add_edge(START, "chatbot")

graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


question = "서울의 유명한 맛집 TOP 10 추천해줘"

for event in graph.stream({"input": [("user", question)]}):
    print(event)