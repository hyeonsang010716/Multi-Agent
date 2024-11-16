from typing import List, TypedDict
from langchain_core.documents import Document

### 다른 그래프를 서브 노드로 사용하는 방법
### 1. state를 상속 받는다. (충돌 때문)
### 2. graph를 노드로 만들어준다.

class SelfRagOverallState(SelfRagState):
    # question: str                       # 사용자의 질문
    # generation: str                     # LLM 생성 답변
    # documents: List[Document]           # 컨텍스트 문서 (검색된 문서)
    # num_generations: int                # 질문 or 답변 생성 횟수 (무한 루프 방지에 활용)
    filtered_documents: List[Document]    # 컨텍스트 문서 중에서 질문에 대답할 수 있는 문서를 필터링
    
    
from langgraph.graph import StateGraph, START, END

#부모 노드
rag_builder = StateGraph(SelfRagOverallState)

#서브 노드 컴파일
tool_search_graph = search_builder.compile()

#서브 노드
rag_builder.add_node("search_data", tool_search_graph) 