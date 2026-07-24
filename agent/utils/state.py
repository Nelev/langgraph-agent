"""Shared agent graph state."""

import operator
from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated


class MessagesState(TypedDict):
    """Conversation state threaded through the agent's graph nodes."""

    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int
