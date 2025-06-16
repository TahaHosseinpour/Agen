from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    openai_api_key="tpsg-DiEk9GvYqybMvtJa64AGzJdeYR6lFfm",
    openai_api_base="https://api.tapsage.com/openai/v1"
)

def chat_node(state: State):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": messages + [response]}

graph_builder = StateGraph(State)
graph_builder.add_node("chat", chat_node)
# graph_builder.set_entry_point("chat")
graph_builder.add_edge(START, "chat")
compiled_graph = graph_builder.compile()

while True:
    user_input = input("👤 You: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    events = compiled_graph.stream({"messages": [{"role": "user", "content": user_input}]})
    for event in events:
        for output in event.values():
            bot_message = output["messages"][-1]
            print("🤖 Bot:", bot_message.content)




#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