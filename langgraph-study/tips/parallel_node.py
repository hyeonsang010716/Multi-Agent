from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, TypedDict, Annotated
from textwrap import dedent

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

# 라우팅 결정을 위한 데이터 모델
class ToolSelector(BaseModel):
    """Routes the user question to the most appropriate tool."""

    tool: Literal["search_menu", "search_web", "search_wine"] = Field(
        description="Select one of the tools: search_menu, search_wine or search_web based on the user's question.",
    )


class ToolSelectors(BaseModel):
    """Select the appropriate tools that are suitable for the user question."""

    tools: List[ToolSelector] = Field(
        description="Select one or more tools: search_menu, search_wine or search_web based on the user's question.",
    )


# 구조화된 출력을 위한 LLM 설정
structured_llm_tool_selector = llm.with_structured_output(ToolSelectors)

# 라우팅을 위한 프롬프트 템플릿
system = dedent(
    """You are an AI assistant specializing in routing user questions to the appropriate tools.
Use the following guidelines:
- For questions about the restaurant's menu, use the search_menu tool.
- For wine recommendations or pairing information, use the search_wine tool.
- For any other information or the most up-to-date data, use the search_web tool.
Always choose the appropriate tools based on the user's question."""
)

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

# 질문 라우터 정의
question_tool_router = route_prompt | structured_llm_tool_selector

# 테스트 실행
print(question_tool_router.invoke({"question": "채식주의자를 위한 메뉴가 있나요?"}))
print(
    question_tool_router.invoke(
        {"question": "스테이크 메뉴의 가격과 어울리는 와인을 추천해주세요."}
    )
)
print(
    question_tool_router.invoke(
        {
            "question": "스테이크 매뉴가 있으면 추천해주세요. 스테이크의 유래에 대해 알려주세요."
        }
    )
)


# 병렬 add_conditional 사용 예시

# def route_datasources_tool_search(state: ToolSearchState) -> Sequence[str]:

#     if set(state['datasources']) == {'search_menu'}:
#         return ['search_menu']

#     elif set(state['datasources']) == {'search_wine'}:
#         return ['search_wine']

#     elif set(state['datasources']) == {'search_web'}:
#         return ['search_web']

#     elif set(state['datasources']) == {'search_menu', 'search_wine'}:
#         return ['search_menu', 'search_wine']
    
#     elif set(state['datasources']) == {'search_menu', 'search_web'}:
#         return ['search_menu', 'search_web']

#     elif set(state['datasources']) == {'search_wine', 'search_web'}:
#         return ['search_wine', 'search_web']

#     return ['search_web', 'search_menu', 'search_wine']

# search_builder.add_conditional_edges(
#     "analyze_question",
#     route_datasources_tool_search,
#     ["search_menu", "search_web", "search_wine"]
# )
