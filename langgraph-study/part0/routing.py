from typing import Literal, Optional, TypedDict
from langgraph.graph import StateGraph, END


# 쿼리에서 "in" 다음에 오는 단어를 찾는 기능
def extract_location(query: str) -> Optional[str]:
    words = query.split()
    if "in" in words:
        index = words.index("in")
        if index + 1 < len(words):
            return words[index + 1]
    return None


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
    query: str
    location: Optional[str]
    forecast: Optional[str]
    response : Optional[str]


# query 추출 노드
def parse_query(state: WeatherState):
    location = extract_location(state["query"])
    return {"location": location}


# 날씨 데이터 가져오는 노드
def get_forecast(state: WeatherState):
    forecast = fetch_weather_data(state["location"])
    return {"forecast": forecast}


# 장소 템플릿
def clarify_location(state: WeatherState):
    clarification = generate_location_clarification(state["location"])
    return {"query": clarification}


# 날씨 템플릿
def generate_response(state: WeatherState):
    response = format_weather_response(state["location"], state["forecast"])
    return {"response": response}


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

graph = graph_builder.compile()

print(graph.invoke({"query": "What's the weather in London?" }))

