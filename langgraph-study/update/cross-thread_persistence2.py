from langgraph.store.memory import InMemoryStore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import uuid
from typing import Annotated
from typing_extensions import TypedDict

from langchain_openai import AzureChatOpenAI
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.base import BaseStore
load_dotenv()

store = InMemoryStore(
    index={
        "embed": OpenAIEmbeddings(model="text-embedding-3-small"),
        "dims": 1536,
    }
)

# Store some memories
store.put(("user_123", "memories"), "1", {"text": "I love pizza"})
store.put(("user_123", "memories"), "2", {"text": "I prefer Italian food"})
store.put(("user_123", "memories"), "3", {"text": "I don't like spicy food"})
store.put(("user_123", "memories"), "3", {"text": "I am studying econometrics"})
store.put(("user_123", "memories"), "3", {"text": "I am a plumber"})

memories = store.search(("user_123", "memories"), query="I like food?", limit=5)

for memory in memories:
    print(f'Memory: {memory.value["text"]} (similarity: {memory.score})')

"""
Memory: I prefer Italian food (similarity: 0.4648266952116817)
Memory: I love pizza (similarity: 0.3551484517438078)
Memory: I am a plumber (similarity: 0.15569870233657104)
"""

"""
InMemoryStore 는 RAG와 비슷한 기능을 한다.
"""