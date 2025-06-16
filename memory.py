from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# ----------- Define the State ----------------

class State(TypedDict):
    messages: Annotated[list, add_messages]  # Used by LangGraph to store conversation history

# ----------- Initialize the LLM ----------------

llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    openai_api_key="tpsg-DiEk9GvYqybMvtJa64AGzJdeYR6lFfm",
    openai_api_base="https://api.tapsage.com/openai/v1"
)

# ----------- Define the Prompt Template ----------------

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer just in Persian Language. Your name is Asa."),
    MessagesPlaceholder("messages")
])

# ----------- Define Chat Node ----------------

def chat_node(state: State):
    # Inject previous messages into prompt
    prompt_value = chat_prompt.invoke({"messages": state["messages"]})
    response = llm.invoke(prompt_value)
    return {"messages": state["messages"] + [response]}  # Append response to state

# ----------- Build the LangGraph ----------------

graph_builder = StateGraph(State)
graph_builder.add_node("chat", chat_node)
graph_builder.add_edge(START, "chat")

# ----------- Add Memory ----------------

memory = MemorySaver()
compiled_graph = graph_builder.compile(checkpointer=memory)

# ----------- Define Config with Thread ID ----------------

config = {"configurable": {"thread_id": "my_conversation"}}

# ----------- Run Interactive Chat ----------------

print("Type 'exit' or 'quit' to stop the chatbot.")

while True:
    user_input = input("👤 You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    # Get previous state from memory
    snapshot = compiled_graph.get_state(config)
    prev_messages = snapshot.values.get("messages", []) if snapshot else []

    # Add new user message
    updated_messages = prev_messages + [{"role": "user", "content": user_input}]

    # Run graph with updated state and config
    events = compiled_graph.stream(
        {"messages": updated_messages},
        config,
        stream_mode="values"
    )

    # Show the last message from the model
    for event in events:
        for output in event.values():
            bot_message = output[-1]  # Last message from the assistant
            print("🤖 Bot:", bot_message.content)
