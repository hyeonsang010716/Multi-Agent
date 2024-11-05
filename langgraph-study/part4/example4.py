from dotenv import load_dotenv
from typing import Annotated, List, Dict
from typing_extensions import TypedDict
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
import feedparser
from urllib.parse import quote
from typing import List, Dict, Optional

load_dotenv()

class GoogleNews:
    """
    구글 뉴스를 검색하고 결과를 반환하는 클래스입니다.
    """

    def __init__(self):
        self.base_url = "https://news.google.com/rss"

    def _fetch_news(self, url: str, k: int = 3) -> List[Dict[str, str]]:
        news_data = feedparser.parse(url)
        return [
            {"title": entry.title, "link": entry.link}
            for entry in news_data.entries[:k]
        ]

    def _collect_news(self, news_list: List[Dict[str, str]]) -> List[Dict[str, str]]:

        if not news_list:
            print("해당 키워드의 뉴스가 없습니다.")
            return []

        result = []
        for news in news_list:
            result.append({"url": news["link"], "content": news["title"]})

        return result

    def search_latest(self, k: int = 3) -> List[Dict[str, str]]:
        url = f"{self.base_url}?hl=ko&gl=KR&ceid=KR:ko"
        news_list = self._fetch_news(url, k)
        return self._collect_news(news_list)

    def search_by_keyword(
        self, keyword: Optional[str] = None, k: int = 3
    ) -> List[Dict[str, str]]:
        if keyword:
            encoded_keyword = quote(keyword)
            url = f"{self.base_url}/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
        else:
            url = f"{self.base_url}?hl=ko&gl=KR&ceid=KR:ko"
        news_list = self._fetch_news(url, k)
        return self._collect_news(news_list)

# 상태 추가
class State(TypedDict):
    messages: Annotated[list, add_messages]
    dummy_data: Annotated[str, "dummy"]

news_tool = GoogleNews()

# 뉴스 검색 툴 추가
@tool
def search_keyword(query: str) -> List[Dict[str, str]]:
    """Look up news by keyword"""
    news_tool = GoogleNews()
    return news_tool.search_by_keyword(query, k=5)

tools = [search_keyword]


llm = ChatOpenAI(model="gpt-4o")

llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {
        "messages": [llm_with_tools.invoke(state["messages"])],
        "dummy_data": "[chatbot] 호출, dummy data",  
    }

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)

# Tool 노드 추가
tool_node = ToolNode(tools=tools)

# Tool을 노드로
graph_builder.add_node("tools", tool_node)

#Tool을 연결
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

#나머지 엣지 추가
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

question = "미국 대선 관련 뉴스 알려줘."

# 초기 입력 상태를 정의
input = State(dummy_data="테스트 문자열", messages=[("user", question)])

# config 설정
config = RunnableConfig(
    recursion_limit=10,  # 최대 10개의 노드까지 방문. 그 이상은 RecursionError 발생
    configurable={"thread_id": "1"}, 
    tags=["my-tag"],
)


"""
stream 에서 사용할 수 있는 매개변수들

input (Union[dict[str, Any], Any]): 그래프에 대한 입력
config (Optional[RunnableConfig]): 실행 구성
stream_mode (Optional[Union[StreamMode, list[StreamMode]]]): 출력 스트리밍 모드
output_keys (Optional[Union[str, Sequence[str]]]): 스트리밍할 키
interrupt_before (Optional[Union[All, Sequence[str]]]): 실행 전에 중단할 노드
interrupt_after (Optional[Union[All, Sequence[str]]]): 실행 후에 중단할 노드
debug (Optional[bool]): 디버그 정보 출력 여부
subgraphs (bool): 하위 그래프 스트리밍 여부
"""

### stream 매개변수들 사용 예시 ###


for event in graph.stream(input=input, config=config): # stream 
    for key, value in event.items():
        print(f"\n[ {key} ]\n")
        if "messages" in value:
            messages = value["messages"]
            value["messages"][-1].pretty_print()


#여기서 상태들을 확인할 수 있음.
print(list(graph.channels.keys()))


print()
print()
print()

# 질문
question = "2024년 노벨 문학상 관련 뉴스를 알려주세요."

# 초기 입력 State 를 정의
input = State(dummy_data="테스트 문자열", messages=[("user", question)])

# config 설정
config = RunnableConfig(
    recursion_limit=10,  # 최대 10개의 노드까지 방문. 그 이상은 RecursionError 발생
    configurable={"thread_id": "1"},  # 스레드 ID 설정
    tags=["my-rag"],  # Tag
)

for event in graph.stream(
    input=input,
    config=config,
    output_keys=["dummy_data"], # 이거를 가지고 출력할 수 있는 범위를 정할 수 있다. 지금은 dummy_data만 출력을 하는 거임
):
    for key, value in event.items():
        print(f"\n[ {key} ]\n")
        if value:
            print(value.keys())
            if "dummy_data" in value:
                print(value["dummy_data"])