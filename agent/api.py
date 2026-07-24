"""FastAPI wrapper that exposes the compiled agent over HTTP."""

from fastapi import FastAPI
from pydantic import BaseModel
from langchain.messages import HumanMessage

from .agent import agent

app = FastAPI(title="ai-agent")


class InvokeRequest(BaseModel):
    """Payload for a single-turn agent call."""

    message: str


class InvokeResponse(BaseModel):
    """The agent's final answer for a single-turn call."""

    response: str


@app.get("/health")
async def health() -> dict[str, str]:
    """Report that the service is up."""
    return {"status": "ok"}


@app.post("/invoke", response_model=InvokeResponse)
async def invoke(request: InvokeRequest) -> InvokeResponse:
    """Run the agent on a single user message and return its final reply."""
    result = await agent.ainvoke({"messages": [HumanMessage(content=request.message)]})
    return InvokeResponse(response=result["messages"][-1].content)
