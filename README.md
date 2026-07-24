# ai-agent

A minimal [LangGraph](https://langchain-ai.github.io/langgraph/) agent that runs locally against an [Ollama](https://ollama.com/) model and can perform basic arithmetic via tool calling.

## How it works

The agent is a small `StateGraph` with a tool-calling loop:

```
START -> llm_call -> should_continue -> tool_node -> llm_call -> ... -> END
```

- **`llm_call`** — sends the conversation to the model, which decides whether to answer directly or call a tool.
- **`should_continue`** — routes to `tool_node` if the last model response contains tool calls, otherwise routes to `END`.
- **`tool_node`** — executes the requested tool(s) and appends the results back into the conversation as `ToolMessage`s, then loops back to `llm_call`.

State is a `MessagesState` TypedDict holding the running message list and an `llm_calls` counter.

### Tools

Three arithmetic tools are exposed to the model ([agent/utils/tools.py](agent/utils/tools.py)):

- `add(a, b)`
- `multiply(a, b)`
- `divide(a, b)`

### Model

The model is wired up via `langchain.chat_models.init_chat_model` targeting a local **Ollama** model (`llama3.1`) with `temperature=0` ([agent/utils/model.py](agent/utils/model.py)).

## Project structure

```
agent/
  agent.py            # builds and compiles the StateGraph (entry point for `langgraph dev`)
  api.py              # FastAPI wrapper exposing the agent over HTTP
  utils/
    model.py           # chat model + tools + tools_by_name
    nodes.py            # llm_call, tool_node, should_continue
    state.py            # MessagesState TypedDict
    tools.py            # add / multiply / divide tool functions
langgraph.json          # graph spec consumed by the LangGraph dev server
main.py                 # placeholder entry point
pyproject.toml           # project metadata and dependencies (uv-managed)
```

## Requirements

- Python 3.14 (see [.python-version](.python-version))
- [uv](https://docs.astral.sh/uv/) for dependency management
- [Ollama](https://ollama.com/) running locally with the `llama3.1` model pulled:

  ```bash
  ollama pull llama3.1
  ```

## Setup

```bash
uv sync
```

## Running the dev server

```bash
uv run langgraph dev
```

This starts the LangGraph in-memory dev server and Studio UI, loading the graph declared in [langgraph.json](langgraph.json) (`agent.agent:agent`).

## Running standalone

`agent/agent.py` can also be run directly, which invokes the agent once with a sample message and renders the graph:

```bash
uv run python -m agent.agent
```

## Running the API wrapper

[agent/api.py](agent/api.py) exposes the agent as a plain HTTP service, as an alternative to the LangGraph dev server:

```bash
uv run serve
```

`serve` is a `[project.scripts]` entry point (see [pyproject.toml](pyproject.toml)) that runs the equivalent of `uvicorn agent.api:app --host 0.0.0.0 --port 8000`.

- `GET /health` — liveness check.
- `POST /invoke` — run the agent on a single message:

  ```bash
  curl -X POST http://localhost:8000/invoke \
    -H "Content-Type: application/json" \
    -d '{"message": "Add 3 and 4."}'
  ```

  Response: `{"response": "..."}`.

Each call is stateless — there is no conversation memory between requests. Multi-turn conversations would require adding a LangGraph checkpointer keyed by a caller-supplied session/thread ID.

## Configuration

Secrets (e.g. `LANGSMITH_API_KEY`) are read from a local `.env` file, which is git-ignored and must not be committed.
