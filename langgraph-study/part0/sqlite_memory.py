import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, END, StateGraph
from typing import Literal, Optional, TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain.schema import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from operator import itemgetter
from dotenv import load_dotenv

load_dotenv()



conn = sqlite3.connect("./sqlite.db" , check_same_thread=False)

# memory = SqliteSaver(conn)
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()


class State(TypedDict):
    messages: Annotated[list, add_messages]
    weather: Optional[str]
    lock: bool

def check_location(state: State) -> Literal["weather_tool", "generate_response"]:
    class QuestionFilterResult(BaseModel):
        result: bool = Field(
            description="Whether the question is about datetime or not"
        )

    output_parser = PydanticOutputParser(pydantic_object=QuestionFilterResult)

    template_str = """당신은 유저의 입력을 보고 날짜와 관련된 질문인지 아닌지 판별해주는 AI입니다.
    
    유저 입력:
    {input}

    {format_instruction}
    """
    model = ChatOpenAI(model="gpt-4o")
    prompt = PromptTemplate(
        template=template_str,
        input_variables=["input"],
        partial_variables={
            "format_instruction": output_parser.get_format_instructions()
        },
    )

    chain = prompt | model | output_parser

    response = chain.invoke({"input": state["messages"][-1]})

    return {"lock" : response.result}


def state_func1(state: State):
    if state["lock"]:
        return "weather_tool"
    else:
        return "generate_response"


def weather_tool(state: State):
    return {"weather": "29999-12-30은 수요일입니다."}


def weather_generate_response(state: State):
    template_str = """당신은 유저가 한 질문에 최대한 친절하고 정확하게 답변을 해주는 AI입니다.
    다음 정보들을 보고 유저의 질문에 답을 해주세요.
    
    유저 입력:
    {input}

    날짜 정보:
    {weather}
    """
    model = ChatOpenAI(model="gpt-4o")
    prompt = PromptTemplate(
        template=template_str,
        input_variables=["input", "weather"],
    )

    chain = (
        prompt
        | model
        | StrOutputParser()
    )

    response = chain.invoke({"input": state["messages"] , "weather" : state["weather"]})

    print("this is response" , response)
    print("state_messages", state["messages"])

    return {"messages": [AIMessage(response)]}


def generate_response(state: State):
    template_str = """당신은 유저가 한 질문에 최대한 친절하고 정확하게 답변을 해주는 AI입니다.
    다음 정보들을 보고 유저의 질문에 답을 해주세요.
    유저의 질문을 절대 출력하지마세요.
    
    유저 입력:
    {input}

    """
    model = ChatOpenAI(model="gpt-4o")
    prompt = PromptTemplate(
        template=template_str,
        input_variables=["input"],
    )

    chain = (
        prompt
        | model
        | StrOutputParser()
    )

    response = chain.invoke({"input" : state["messages"]})
    print("this is response" , response)
    return {"messages": [AIMessage(response)]}


graph_builder = StateGraph(State)

graph_builder.add_node("check_location", check_location)
graph_builder.add_node("weather_tool", weather_tool)
graph_builder.add_node("weather_generate_response", weather_generate_response)
graph_builder.add_node("generate_response", generate_response)

graph_builder.add_conditional_edges(
    source="check_location",
    path=state_func1,
    path_map={"weather_tool": "weather_tool", "generate_response": "generate_response"},
)

graph_builder.add_edge(START, "check_location")
graph_builder.add_edge("weather_tool", "weather_generate_response")
graph_builder.add_edge("weather_generate_response", END)
graph_builder.add_edge("generate_response", END)


graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}


# print(graph.invoke({"messages": ["29999년12월30일은 무슨 요일이야?"]}, config,))

# print(graph.invoke({"messages": ["내가 무슨 질문을 했었지?"]}, config,))
for chunk_msg, metadata in graph.stream(
    {"messages": ["29999년12월30일은 무슨 요일이야?"]}, config, stream_mode="messages"
):  
    if metadata["langgraph_node"] == "weather_generate_response":
        if chunk_msg.content:
            print(chunk_msg.content, end="", flush=True)

    if metadata["langgraph_node"] == "generate_response":
        if chunk_msg.content:
            print(chunk_msg.content, end="", flush=True)

for chunk_msg, metadata in graph.stream(
    {"messages": ["내가 무슨 질문을 했었지?"]}, config, stream_mode="messages"
):  
    if metadata["langgraph_node"] == "weather_generate_response":
        if chunk_msg.content:
            print(chunk_msg.content, end="", flush=True)

    if metadata["langgraph_node"] == "generate_response":
        if chunk_msg.content:
            print(chunk_msg.content, end="", flush=True)
