from langgraph_sdk import get_client
URL = "http://localhost:61198"
client = get_client(url=URL)
assistants = client.assistants.search()
print(assistants)