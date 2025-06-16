from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
import os

# Tavily API KEY
os.environ["TAVILY_API_KEY"] = "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"

# Metis Model
llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    openai_api_key="tpsg-DiEk9GvYqybMvtJa64AGzJdeYR6lFfm",
    openai_api_base="https://api.tapsage.com/openai/v1"
)

# Search Tool Tavily
tool = TavilySearch(max_results=2)
tools = [tool]

# Connect tools to model
llm_with_tools = llm.bind_tools(tools)

# State Definition
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Node : Chat
def chat_node(state: State):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": messages + [response]}

# Node : Tool
tool_node = ToolNode(tools=tools)

# Graph Building
graph_builder = StateGraph(State)
graph_builder.add_node("chat", chat_node)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chat", tools_condition)
graph_builder.add_edge("tools", "chat")
graph_builder.add_edge(START, "chat")
compiled_graph = graph_builder.compile()

# Start the conversation loop
while True:
    user_input = input("👤 You: ")

    # Exit command
    if user_input.lower() in ["exit", "quit"]:
        break

    # Start streaming the graph with the user input
    events = compiled_graph.stream({
        "messages": [{"role": "user", "content": user_input}]
    })

    # Process and display the LLM's responses
    for event in events:
        for output in event.values():
            response = output["messages"][-1]
            print("🤖 Bot:", response.content)

