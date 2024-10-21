from swarm import Swarm, Agent

client = Swarm()

english_agent = Agent(
    name="English Agent",
    instructions="You are a supervisor who calls 'transfer_to_agent' whenever English is detected in the input."
)

korea_agent = Agent(
    name="Korean Agent",
    instructions="You only speak Koearn.",
)


def transfer_to_korea_agent():
    """Transfer english speaking users immediately."""
    return korea_agent


english_agent.functions.append(transfer_to_korea_agent)

messages = [{"role": "user", "content": "Hello"}]
response = client.run(agent=english_agent, messages=messages)

print(response.messages[-1]["content"])



from langchain_teddynote.messages import display_message_tree


display_message_tree(response.messages)