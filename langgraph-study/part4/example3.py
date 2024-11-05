# LangGraph 메모리 저장 예시

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_teddynote.tools.tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()
# 메모리 저장소 생성
memory = MemorySaver()
#상태
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 도구 초기화
tool = TavilySearch(max_results=3)
tools = [tool]

# LLM 초기화
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools)

# 메시지 전달
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Node 초기화
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

# 도구 초기화 : ToolNode 를 사용함
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

# 도구 상태 연결 : tools_condition 사용
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

# 엣지 연결
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# 그래프 메모리 연결
graph = graph_builder.compile(checkpointer=memory)


#### 대화 예시 ####

from langchain_core.runnables import RunnableConfig

config = RunnableConfig(
    recursion_limit=10,  # 최대 10개의 노드까지 방문. 그 이상은 RecursionError 발생
    configurable={"thread_id": "1"},  # 스레드 ID 설정
)

#질문 1
question = (
    "내 이름은 현상 입니다. LLM 개발자에요. 만나서 반가워요"
)

for event in graph.stream({"messages": [("user", question)]}, config=config):
    for value in event.values():
        value["messages"][-1].pretty_print()


#질문2
question = "내 이름이 뭐라고 했지?"

config = RunnableConfig(
    recursion_limit=10,  # 최대 10개의 노드까지 방문. 그 이상은 RecursionError 발생
    configurable={"thread_id": "2"},  # 스레드 ID 설정
)

for event in graph.stream({"messages": [("user", question)]}, config=config):
    for value in event.values():
        value["messages"][-1].pretty_print()