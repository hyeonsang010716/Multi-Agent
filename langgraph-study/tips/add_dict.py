import asyncio
from typing import Dict, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph.message import add_messages
import operator
import os


## 딕셔너리 업데이트 하는 방법
def merge_dicts(left: Dict, right: Dict) -> Dict:
    return {**left, **right}

class State(TypedDict):
    results: Annotated[Dict[str, str], merge_dicts]
    
    
    
def write_newsletter_section(state: State, sub_theme: str) -> Dict:
    articles = state['sub_theme_articles'][sub_theme]
    
    # Prepare a list of formatted article references including title, image, and a snippet of raw content
    article_references = "\n".join(
        [f"Title: {article['title']}\nContent: {article['raw_content']}..."
         for article in articles]
    )
    
    prompt = f"""
    Write a newsletter section for the sub-theme: "{sub_theme}".
    
    Use the following articles as reference and include relevant points from both their titles, images, and content:
    <article>
    {article_references}
    <article/>
    Summarize the key points and trends related to this sub-theme, and ensure you reference the images where they add value to the discussion. 
    Keep the tone engaging and informative for newsletter readers. You should write in Korean
    """
    
    messages = [HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    return {"results": {sub_theme: response.content}}