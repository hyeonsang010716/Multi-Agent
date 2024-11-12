from typing import Literal, Optional, TypedDict , Annotated
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph.message import add_messages
from operator import itemgetter
from langchain_core.messages import RemoveMessage
from langchain.schema import HumanMessage, AIMessage
load_dotenv()


# 쿼리에서 "in" 다음에 오는 단어를 찾는 기능
def extract_location(query: str) -> Optional[str]:
    return "London"


# 위치가 3글자 미만이면 애매한 것으로 간주
def is_ambiguous(location: str) -> bool:

    return len(location) < 3


# 간단한 모의 날씨 데이터
def fetch_weather_data(location: str) -> str:
    weather_data = {
        "New York": "Sunny, 25°C",
        "London": "Rainy, 15°C",
        "Tokyo": "Cloudy, 20°C",
        "Paris": "Partly cloudy, 22°C",
    }
    return weather_data.get(location, "Weather data not available")


def generate_location_clarification(location: str) -> str:
    return f"Could you please provide more details about the location '{location}'?"


def format_weather_response(location: str, forecast: str) -> str:
    return f"The weather in {location} is: {forecast}"


# 2. 노드 정의
class WeatherState(TypedDict):
    messages: Annotated[list, add_messages]
    location: Optional[str]
    forecast: Optional[str]


# query 추출 노드
def parse_query(state: WeatherState):
    location = extract_location(state["messages"][-1])
    return {"location": location}


# 날씨 데이터 가져오는 노드
def get_forecast(state: WeatherState):
    # print("example state.values" , state.values.get('user_name'))
    forecast = fetch_weather_data(state["location"])
    return {"forecast": forecast}


# 장소 템플릿
def clarify_location(state: WeatherState):
    clarification = generate_location_clarification(state["location"])
    for m in state["messages"] : RemoveMessage(id=m.id)
    return {"messages": [clarification]}


# 날씨 템플릿
def generate_response(state: WeatherState):
    # response = format_weather_response(state["location"], state["forecast"])
    template_str = """당신은 유저의 질문과 제공되는 정보를 가지고 유저가 원하는 답변을 생성해주는 AI 입니다.
    
    유저 입력:
    {input}

    정보:
    {location}
    {forecast}

    한국어로 답변하세요.
    """
    model = ChatOpenAI(model="gpt-4o")
    prompt = PromptTemplate(
        template=template_str, input_variables=["input", "location", "forecast"]
    )
    chain = (
        {
            "input": itemgetter("messages"),
            "location": itemgetter("location"),
            "forecast": itemgetter("forecast"),
        }
        | prompt
        | model
        | StrOutputParser()
    )
    response = chain.invoke(state)
    return {"messages": AIMessage(response)}


# 노드 상태 함수
def check_location(state: WeatherState) -> Literal["valid", "invalid", "ambiguous"]:
    if not state["location"]:
        return "invalid"
    elif is_ambiguous(state["location"]):
        return "ambiguous"
    else:
        return "valid"


from langgraph.graph import StateGraph, START, END

graph_builder = StateGraph(WeatherState)

graph_builder.add_node("parse_query", parse_query)
graph_builder.add_node("clarify_location", clarify_location)
graph_builder.add_node("get_forecast", get_forecast)
graph_builder.add_node("generate_response", generate_response)

graph_builder.add_conditional_edges(
    source="parse_query",
    path=check_location,
    path_map={"valid": "get_forecast", "ambiguous": "clarify_location", "invalid": END},
)

graph_builder.add_edge(START, "parse_query")
graph_builder.add_edge("get_forecast", "generate_response")
graph_builder.add_edge("generate_response", END)

from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

graph = graph_builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}

output = graph.invoke({"messages": ["What's the weather in London"]}, config=config)

for event in output["messages"]:
    print(event.content)

output = graph.invoke({"messages": ["내가 방금 무슨 질문 했었지?"]}, config=config)

for event in output["messages"]:
    print(event.content)

#마지막 응답만 출력
for chunk_msg, metadata in graph.stream({"messages": ["거기 날씨가 뭐라고?"]}, config, stream_mode="messages"):
    if metadata["langgraph_node"] == "generate_response":
        if chunk_msg.content:
            print(chunk_msg.content, end="", flush=True)
    else:
        print(chunk_msg.content)