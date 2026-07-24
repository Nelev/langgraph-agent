from langchain.chat_models import init_chat_model
from .tools import add, multiply, divide

model = init_chat_model(
    "llama3.1",
    model_provider="ollama",
    temperature=0
)

# Augment the LLM with tools
tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)
