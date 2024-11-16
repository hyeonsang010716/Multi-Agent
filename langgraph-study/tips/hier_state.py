from typing import List, TypedDict, Annotated
from langchain_core.documents import Document
from operator import add

class SearchState(TypedDict):
    question: str                                            
    documents: Annotated[List[Document], add]     # 컨텍스트 문서를 추가 
    filtered_documents: List[Document] 
    
    
# 기존 SearchState 상속해서 새로 정의
class ToolSearchState(SearchState): 
    # question: str                                              
    # documents: Annotated[List[Document], add]     # 컨텍스트 문서를 추가 
    # filtered_documents: List[Document]            # 컨텍스트 문서 중에서 질문에 대답할 수 있는 문서를 필터링
    datasources: List[str]    