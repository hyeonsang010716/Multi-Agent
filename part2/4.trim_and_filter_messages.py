from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage , SystemMessage
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('AZURE_OPENAI_API_KEY')
endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
str_apiversion = os.getenv("OPENAI_API_VERSION")

messages = [SystemMessage("너는 AI 봇이야. 한국어로 답변해줘." , name = "Bot" ) , AIMessage(f"So you said you were researching ocean mammals?", name="Bot")]

messages.append(HumanMessage(f"Yes, I know about whales. But what others should I learn about?", name="Lance"))

# for m in messages:
#     m.pretty_print()

model = AzureChatOpenAI(
    azure_deployment="gpt-4o",
    azure_endpoint = endpoint,
    api_key = api_key,
    api_version =str_apiversion,
    temperature=0.2,
)

#output = model.invoke(messages)

# print(output.content)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------LangGraph

from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END

# Node
def chat_model_node(state: MessagesState):
    return {"messages": model.invoke(state["messages"])}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)

graph = builder.compile()

# output = graph.invoke({"messages" : messages})

# print(output['messages'])


#---------------------------------------------------------------------------------------------------------------------------------------------------------------
from langchain_core.messages import RemoveMessage

# Nodes
def filter_messages(state: MessagesState):
    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"messages": delete_messages}

def chat_model_node(state: MessagesState):
    return {"messages": [model.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("filter", filter_messages)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "filter")
builder.add_edge("filter", "chat_model")
builder.add_edge("chat_model", END)

graph = builder.compile()

# Message list with a preamble
messages = [AIMessage("Hi.", name="Bot", id="1")]

messages.append(HumanMessage("Hi.", name="Lance", id="2"))
messages.append(AIMessage("So you said you were researching ocean mammals?", name="Bot", id="3"))
messages.append(HumanMessage("Yes, I know about whales. But what others should I learn about? 한국어로 답변해줘.", name="Lance", id="4"))

# Invoke
output = graph.invoke({'messages': messages})
# for m in output['messages']:
#     m.pretty_print()

messages.append(output['messages'][-1])
messages.append(HumanMessage("Tell me more about Narwhals!", name="Lance"))

# output = graph.invoke({'messages': messages})
# for m in output['messages']:
#     m.pretty_print()

#---------------------------------------------------------------------------------------Add trim
from langchain_core.messages import trim_messages
from langchain_openai import ChatOpenAI
# Node
def chat_model_node(state: MessagesState):
    messages = trim_messages(
        state["messages"],
        max_tokens=100,
        strategy="last",
        token_counter=ChatOpenAI(model="gpt-4o"),
        allow_partial=True,
    )
    return {"messages": [model.invoke(messages)]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_node)
builder.add_edge(START, "chat_model")
builder.add_edge("chat_model", END)

graph = builder.compile()

trim_output = graph.invoke({'messages': messages})

for m in trim_output['messages']:
    m.pretty_print()

#trim을 사용하면 삭제되었던 메시지도 다시 다 출력된다.
#trim 사용할 때 주의할 점은 AzureChatOpenAI는 지원하지 않는다.