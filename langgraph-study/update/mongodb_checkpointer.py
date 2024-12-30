from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage, AIMessage
from fastapi import File, UploadFile
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from pymongo import AsyncMongoClient
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START
from dotenv import load_dotenv
import os
load_dotenv()

async def main():

    client = AsyncMongoClient("mongodb://127.0.0.1:27017/")
    checkpointer = AsyncMongoDBSaver(client)


    model = AzureChatOpenAI(model="gpt-4o", temperature=0)  


    def call_model(state: MessagesState):
        system_msg = f"You are a helpful assistant talking to the user."

        response = model.invoke(
            [{"type": "system", "content": system_msg}] + state["messages"]
        )

        return {"messages": response}


    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_edge(START, "call_model")

    graph = builder.compile(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "2"}}

    response = await graph.ainvoke({"messages": [("user", "my name is hyeonsang?")]}, config)
    
    print(await graph.aget_state(config))

# 비동기 함수 실행
import asyncio
asyncio.run(main())