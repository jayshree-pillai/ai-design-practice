# LangChain — Must-Memorize Snippets

Each Python snippet runs independently after setup.

## Setup

```bash
pip install langchain langchain-openai python-dotenv pydantic azure-search-documents
```

Create `.env`:
```env
OPENAI_API_KEY=your-key
```

## 1. Call a model

```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
model = ChatOpenAI(model="gpt-5-nano")

response = model.invoke("Explain revenue in one sentence.")
print(response.text)
```

**Critical notes:**

- `response` is an `AIMessage`; `.text` extracts its text.
- `load_dotenv()` loads `.env` into environment variables; the model reads `OPENAI_API_KEY`.

## 2. Prompt → model → string

```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
model = ChatOpenAI(model="gpt-5-nano")

prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize the report in one sentence."),
    ("human", "Company: {company}\nReport: {report_text}"),
])

chain = prompt | model | StrOutputParser()

answer = chain.invoke({
    "company": "Acme",
    "report_text": "Revenue grew 12%.",
})

print(answer)
```

**Critical notes:**

- The chain's first step determines its input; dictionary keys must match prompt variables.
- `prompt.invoke(...)` only formats messages. The model generates the answer; `StrOutputParser()` returns its text as a string.

## 3. Structured output

```python
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

class Report(BaseModel):
    company: str
    growth_percent: float = Field(description="Use 12 for 12%.")

load_dotenv()
model = ChatOpenAI(model="gpt-5-nano")
structured_model = model.with_structured_output(Report)

result = structured_model.invoke("Acme's revenue grew 12%.")

print(result.company)
print(result.growth_percent)
```

**Critical notes:**

- Passing a Pydantic class returns a validated object of that class.
- Schema validation checks structure and types, not factual accuracy.

## 4. RunnableLambda

```python
from langchain_core.runnables import RunnableLambda

prepare = RunnableLambda(
    lambda text: {"report_text": text.strip()}
)

result = prepare.invoke("  Revenue grew 12%.  ")
print(result)
# {"report_text": "Revenue grew 12%."}
```

**Critical note:** Wraps a Python function so it can participate in a runnable chain. It does not inherently call a model.

## 5. RunnableParallel

```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel

load_dotenv()
model = ChatOpenAI(model="gpt-5-nano")

prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize the report in one sentence."),
    ("human", "{report_text}"),
])

summary_chain = prompt | model | StrOutputParser()

parallel = RunnableParallel(
    summary=summary_chain,
    character_count=RunnableLambda(
        lambda data: len(data["report_text"])
    ),
)

result = parallel.invoke({"report_text": "Revenue grew 12%."})

print(result["summary"])
print(result["character_count"])  # 17
```

**Critical notes:**

- Both branches receive the same original input and run concurrently.
- One branch cannot use the other branch's result; the character count measures the original report.

## 6. Extract, pass through, and assign

```python
from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough

data = {"question": "  What was revenue?  "}

print(itemgetter("question")(data))
print(RunnablePassthrough().invoke(data))

enrich = RunnablePassthrough.assign(
    search_query=lambda data: data["question"].strip()
)

print(enrich.invoke(data))
# {
#     "question": "  What was revenue?  ",
#     "search_query": "What was revenue?"
# }
```

**Critical notes:**

- `itemgetter("question")` extracts one value; `RunnablePassthrough()` passes through the entire input.
- `.assign()` requires a dictionary and adds or overwrites keys in the returned dictionary.
- Fields computed in the same `.assign()` cannot use each other's newly computed values.

## 7. Batch

```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
model = ChatOpenAI(model="gpt-5-nano")

responses = model.batch(
    ["Define revenue.", "Define profit."],
    config={"max_concurrency": 2},
)

for response in responses:
    print(response.text)
```

**Critical note:** Results preserve input order even if calls finish in a different order. `max_concurrency` limits simultaneous work.

## 8. Async invocation and batch

```python
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
model = ChatOpenAI(model="gpt-5-nano")

async def main():
    response = await model.ainvoke("Define revenue.")
    print(response.text)

    responses = await model.abatch(
        ["Define revenue.", "Define profit."],
        config={"max_concurrency": 2},
    )
    for response in responses:
        print(response.text)

asyncio.run(main())
```

**Critical notes:**

- Calling `ainvoke(...)` only creates a coroutine; await or schedule it to execute.
- Consecutive `await` calls run sequentially. `abatch()` handles multiple inputs concurrently.
- In a notebook with an active event loop, use `await main()` instead of `asyncio.run(main())`.

  
| Command | What it does |
|---|---|
| `asyncio.run(main())` | **Creates** an event loop → runs `main()` → **closes** the loop afterward |
| `await main()` | Runs `main()` using the **existing** event loop; waits for its result while allowing other async tasks to run |

## 9. Streaming

```python
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
model = ChatOpenAI(model="gpt-5-nano")

for chunk in model.stream("Explain revenue briefly."):
    print(chunk.text, end="", flush=True)
print()

async def main():
    async for chunk in model.astream("Explain profit briefly."):
        print(chunk.text, end="", flush=True)
    print()

asyncio.run(main())
```

**Critical note:** Direct model streaming yields `AIMessageChunk` objects. Streaming a chain ending with `StrOutputParser()` yields strings.

## 10. Manual two-tool execution loop

```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage

@tool
def get_revenue(company: str, year: int):
    """Get a company's annual revenue."""
    data = {("ACME", 2024): 100000}
    return data.get((company.strip().upper(), year))

@tool
def get_employee(company: str, year: int):
    """Get a company's employee count."""
    data = {("ACME", 2024): 100}
    return data.get((company.strip().upper(), year))

load_dotenv()
model = ChatOpenAI(model="gpt-5-nano")

tools = [get_revenue, get_employee]
model_with_tools = model.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}

messages = [
    HumanMessage(
        content="Use both tools: Acme's revenue and employee count for 2024."
    )
]

for _ in range(5):
    response = model_with_tools.invoke(messages)
    messages.append(response)

    if not response.tool_calls:
        print(response.text)
        break

    for call in response.tool_calls:
        selected_tool = tools_by_name[call["name"]]
        result = selected_tool.invoke(call["args"])

        messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=call["id"],
            )
        )
else:
    raise RuntimeError("No final answer within 5 model calls.")
```

**Critical notes:**

- Binding tools lets the model request them; `selected_tool.invoke(...)` actually executes them.
- Append the model's message before its tool results; match each result using `tool_call_id`.
- Handle every tool call in the response.
- The `else` belongs to the outer loop and runs when all five iterations finish without `break`.

## 11. create_agent

```python
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

@tool
def get_revenue(company: str, year: int):
    """Get a company's annual revenue."""
    data = {("ACME", 2024): 100000}
    return data.get((company.strip().upper(), year))

@tool
def get_employee(company: str, year: int):
    """Get a company's employee count."""
    data = {("ACME", 2024): 100}
    return data.get((company.strip().upper(), year))

load_dotenv()
model = ChatOpenAI(model="gpt-5-nano")

agent = create_agent(
    model=model,
    tools=[get_revenue, get_employee],
    system_prompt="Use tools to look up company figures. Do not guess.",
)

result = agent.invoke({
    "messages": [
        HumanMessage(
            content="Find Acme's revenue and employee count for 2024."
        )
    ]
})

print(result["messages"][-1].text)
```

**Critical notes:**

- The agent manages tool execution, tool-result messages, and repeated model calls.
- Its result is a state dictionary, not a single `AIMessage`.

## 12. Azure Search → context → answer

Add to `.env`:
```env
AZURE_SEARCH_ENDPOINT=https://your-service.search.windows.net
AZURE_SEARCH_INDEX=your-index
AZURE_SEARCH_API_KEY=your-search-key
```

```python
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX"],
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]),
)

model = ChatOpenAI(model="gpt-5-nano")

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer only from context. If insufficient, say you don't know."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])

chain = prompt | model | StrOutputParser()
question = "What was Acme's revenue in 2024?"

results = client.search(
    search_text=question,
    search_fields=["content"],
    select=["content"],
    top=3,
)

context = "\n\n".join(
    row["content"] for row in results if row.get("content")
)

if context.strip():
    answer = chain.invoke({"context": context, "question": question})
    print(answer)
else:
    print("No matching content found.")
```

**Critical notes:**

- Requires an existing index with a searchable, retrievable text field named `content`.
- `search_fields` controls where to search; `select` controls which fields are returned.
- This uses keyword search, with Azure Search retrieving evidence and OpenAI generating the answer.

# LangGraph — Must-Memorize Interview Snippets

Memorize these 8 patterns in order. Each Python block is standalone.

Keep required state/tool annotations; skip optional function annotations.

## 1. Build a Graph, Return Updates, and Choose the Next Node

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    question: str
    prompt: str

def clean(state):
    return {"question": state["question"].strip()}

def route(state):
    return "build_prompt" if state["question"] else END

def build_prompt(state):
    return {"prompt": f"Answer: {state['question']}"}

builder = StateGraph(State)
builder.add_node("clean", clean)
builder.add_node("build_prompt", build_prompt)
builder.add_edge(START, "clean")
builder.add_conditional_edges("clean", route)
builder.add_edge("build_prompt", END)

graph = builder.compile()
data = {"question": "  What was revenue?  ", "prompt": ""}

for update in graph.stream(data, stream_mode="updates"):
    print(update)
```

**Critical notes:**

- Nodes return **partial state updates**; omitted fields retain their values.
- Routers return **destinations**, not state updates.
- `compile()` builds the runnable graph; it does not execute it.
- `graph.invoke(data)` executes the graph and returns the final state.
- Iterating over `graph.stream(...)` executes the graph while yielding progress.
- `"updates"` gives node updates; `"values"` gives full state snapshots.
- Calling `invoke()` and then `stream()` executes the graph twice.

## 2. Parallel Branches → Reducer → Join

```python
from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    evidence: Annotated[list[str], add]
    summary: str

def revenue(state):
    return {"evidence": ["Revenue grew 12%"]}

def debt(state):
    return {"evidence": ["Debt fell 5%"]}

def summarize(state):
    return {"summary": "; ".join(state["evidence"])}

builder = StateGraph(State)
builder.add_node("revenue", revenue)
builder.add_node("debt", debt)
builder.add_node("summarize", summarize)
builder.add_edge(START, "revenue")
builder.add_edge(START, "debt")
builder.add_edge(["revenue", "debt"], "summarize")
builder.add_edge("summarize", END)

graph = builder.compile()
print(graph.invoke({"evidence": [], "summary": ""}))
```

**Critical notes:**

- Concurrent updates to the same field need a suitable reducer.
- `Annotated[list[str], add]` combines lists using concatenation.
- Return **only new items**; returning existing items again causes duplication.
- `add_edge(["revenue", "debt"], "summarize")` waits for both branches.
- Parallel nodes see the state available at the start of their step.
- LangGraph collects their updates and applies the reducer.
- This does not protect external shared mutable objects from races.
- Do not infer completion order from the final list order.

## 3. MessagesState + Checkpointing + Thread ID

```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver

def reply(state):
    return {"messages": [{"role": "assistant", "content": "Noted."}]}

builder = StateGraph(MessagesState)
builder.add_node("reply", reply)
builder.add_edge(START, "reply")
builder.add_edge("reply", END)

graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "chat-1"}}

graph.invoke(
    {"messages": [{"role": "user", "content": "Review revenue."}]},
    config
)

result = graph.invoke(
    {"messages": [{"role": "user", "content": "Also review debt."}]},
    config
)

print(len(result["messages"]))  # 4
```

**Critical notes:**

- Same `thread_id` + same checkpointer → saved conversation state.
- A different `thread_id` separates the conversation state.
- Send **new messages only**.
- `MessagesState` uses the `add_messages` reducer.
- A new message ID appends a message.
- An existing message ID replaces that message in its existing position.
- Matching is by **ID**, not by message text.
- `thread_id` identifies the conversation; message `id` identifies one message.
- `InMemorySaver` loses data when the process ends.

## 4. Model → Tools → Model Loop

Requires `langgraph`, `langchain`, `langchain-openai`, and `OPENAI_API_KEY`.

```python
from langgraph.graph import StateGraph, MessagesState, START
from langchain.tools import tool, ToolNode
from langchain.tools.tool_node import tools_condition
from langchain_openai import ChatOpenAI

@tool
def get_revenue(company: str, year: int):
    """Look up annual revenue in USD."""
    return {("Acme", 2025): 120_000_000}.get((company, year))

model = ChatOpenAI(model="gpt-5-nano").bind_tools([get_revenue])

def call_model(state):
    return {"messages": [model.invoke(state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode([get_revenue]))
builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition)
builder.add_edge("tools", "model")

graph = builder.compile()
result = graph.invoke(
    {"messages": [{
        "role": "user",
        "content": "Use get_revenue for Acme's 2025 revenue."
    }]},
    config={"recursion_limit": 10}
)

print(result["messages"][-1].content)
```

**Critical notes:**

- The model requests tool calls; `ToolNode` executes them.
- `tools_condition` routes to `"tools"` when the model requests a tool.
- Otherwise, `tools_condition` routes to `END`.
- Keep the node named `"tools"` with this default routing.
- The `"tools" → "model"` edge lets the model use the tool results.
- `recursion_limit` limits graph supersteps, not individual tool calls.
- Exceeding the limit raises `GraphRecursionError`.

## 5. Pause → Inspect → Resume → Inspect History

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

class State(TypedDict):
    report: str
    status: str

def review(state):
    approved = interrupt({"report": state["report"]})
    return {"status": "approved" if approved else "rejected"}

builder = StateGraph(State)
builder.add_node("review", review)
builder.add_edge(START, "review")
builder.add_edge("review", END)

graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "report-1"}}

paused = graph.invoke(
    {"report": "Revenue grew 12%.", "status": "pending"},
    config
)

print(paused["__interrupt__"])
# [Interrupt(value={'report': 'Revenue grew 12%.'}, id='<generated-id>', response_schema=None)]

snapshot = graph.get_state(config)

print(snapshot.values, snapshot.next)
# {'report': 'Revenue grew 12%.', 'status': 'pending'} ('review',)
# State is still pending; review must resume.

result = graph.invoke(Command(resume=True), config)

print(result["status"])
# approved

for snapshot in graph.get_state_history(config):
    print(snapshot.values, snapshot.next)

# Prints these three lines, newest first:
# {'report': 'Revenue grew 12%.', 'status': 'approved'} ()
# {'report': 'Revenue grew 12%.', 'status': 'pending'} ('review',)
# {} ('__start__',)
```

**Critical notes:**

- `interrupt()` pauses execution and exposes its payload to the caller.
- Both `resume=True` and `resume=False` continue execution.
- The resume value becomes the return value of `interrupt()`.
- **Your code** maps that value to `"approved"` or `"rejected"`.
- Resume with the same thread/checkpointer.
- The interrupted node restarts from its beginning.
- Side effects before `interrupt()` can therefore repeat.
- `snapshot.values` contains saved state.
- `snapshot.next` contains pending node names.
- An empty `snapshot.next` means no pending work, not necessarily business success.
- `get_state_history()` returns checkpoints newest first.
- Reading state or history does not execute the graph.

## 6. Update State and Route in the Same Node

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

class State(TypedDict):
    approved: bool
    status: str

def decide(state):
    if state["approved"]:
        return Command(update={"status": "approved"}, goto="finish")
    return Command(update={"status": "rejected"}, goto=END)

def finish(state):
    print(state["status"])
    return {}

builder = StateGraph(State)
builder.add_node("decide", decide)
builder.add_node("finish", finish)
builder.add_edge(START, "decide")
builder.add_edge("finish", END)

graph = builder.compile()
print(graph.invoke({"approved": True, "status": "pending"}))
```

**Critical notes:**

- `Command(update=..., goto=...)` updates state and chooses the next destination.
- Return it **from a node**.
- `Command(resume=...)` serves a different purpose: pass it **to the graph** to resume an interrupt.
- `goto` does not cancel static outgoing edges.
- Do not add an unconditional `"decide" → "finish"` edge here.
- Plain `Command(update=..., goto=...)` does not require a checkpointer.

## 7. Retry a Failing Node

```python
from itertools import count
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy

class State(TypedDict):
    revenue: int

attempts = count(1)

def fetch_revenue(state):
    if next(attempts) < 3:
        raise TimeoutError("Service unavailable")
    return {"revenue": 120_000_000}

builder = StateGraph(State)
builder.add_node(
    "fetch_revenue",
    fetch_revenue,
    retry_policy=RetryPolicy(
        max_attempts=3,
        retry_on=TimeoutError
    )
)
builder.add_edge(START, "fetch_revenue")
builder.add_edge("fetch_revenue", END)

graph = builder.compile()
print(graph.invoke({"revenue": 0}))
```

**Critical notes:**

- `max_attempts=3` means **one initial attempt + two retries**.
- The node must raise an exception matching `retry_on`.
- Returning an error dictionary does not trigger retries.
- The failing node is retried, not the entire graph from `START`.
- External side effects can repeat; retries do not undo them.
- If all attempts fail, the exception propagates.
- The counter only simulates failures.
- A retry policy does not itself impose an execution timeout.

## 8. Dynamic Parallel Work with Send

```python
from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

class State(TypedDict):
    companies: list[str]
    results: Annotated[list[str], add]

def dispatch(state):
    return [
        Send("review_company", {"company": company})
        for company in state["companies"]
    ]

def review_company(state):
    return {"results": [f"{state['company']}: reviewed"]}

builder = StateGraph(State)
builder.add_node("review_company", review_company)
builder.add_conditional_edges(START, dispatch)
builder.add_edge("review_company", END)

graph = builder.compile()
result = graph.invoke({
    "companies": ["Acme", "Globex"],
    "results": []
})
print(sorted(result["results"]))
```

**Critical notes:**

- Register one worker node; execute it multiple times.
- Each `Send` specifies a destination and that worker's input.
- The worker receives the custom payload, not automatically the entire parent state.
- The reducer combines the workers' returned results.
- Return singleton lists containing only each worker's new result.
- One worker reaching `END` does not cancel the other workers.
- Do not depend on parallel completion order.
- `sorted()` here only makes the displayed output predictable.

## Practice Priority

Rebuild patterns **1–5 without looking**, then explain:

- Why concurrent writes need a reducer.
- How a thread ID connects calls to saved state.
- How the tool loop decides when to stop.
- Why code before an interrupt can execute again.

Then practice patterns **6–8**.

# Pydantic v2 — Must-Memorize Interview Snippets

Practice snippets 1–5 first, then aliases and discriminated unions. Each code block stands on its own.
```python snippets
import json
from typing import Literal
from pydantic import (
    BaseModel, ConfigDict, Field, ValidationError,
    field_validator, model_validator,
)


# Supporting models: two possible shapes for a nested source.
class FileSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["file"]  # Accepts exactly "file".
    filename: str
    page: int = Field(ge=1)  # Must be >= 1.


class WebSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: Literal["web"]
    url: str  # Checks string type, not URL syntax.


# MAIN MODEL: combines the interview topics.
class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Reject unknown keys.

    question: str = Field(min_length=1)  # No default -> required.

    top_k: int = Field(
        default=5,     # Used when input omits this field.
        ge=1, le=20,   # Allowed range: 1 through 20.
        strict=True,   # Reject "3" and True; require an integer.
        alias="topK",  # Input key: topK. Python attribute: top_k.
    )

    start_year: int  # Non-strict: "2024" can become integer 2024.
    end_year: int

    note: str | None = None  # Can be omitted OR explicitly be None.
    # Without "= None", this field would be required but nullable.

    tags: list[str] = Field(default_factory=list)
    # Creates a fresh list per instance. Pass list, not list().

    source: FileSource | WebSource = Field(discriminator="kind")
    # Nested dictionary becomes a model.
    # kind="file" chooses FileSource; kind="web" chooses WebSource.

    @field_validator("question", mode="before")
    @classmethod
    def trim_question(cls, value):
        # BEFORE: receives raw input before type/constraint checks.
        if isinstance(value, str):
            return value.strip()
        return value  # Let Pydantic reject invalid types.

    # Field validators return the field value.
    # Default mode="after" receives the already parsed value.

    @model_validator(mode="after")
    def check_year_range(self):
        # AFTER: receives self after the fields validate.
        # Use this for rules involving multiple fields.
        if self.end_year < self.start_year:
            raise ValueError("end_year must be >= start_year")
        return self  # Model after-validator must return the instance.


payload = {
    "question": "  What was revenue?  ",
    "topK": 3,
    "start_year": "2024",
    "end_year": 2025,
    "source": {
        "kind": "file",
        "filename": "annual_report.pdf",
        "page": 3,
    },
}

# 1. DICTIONARY -> VALIDATED MODEL INSTANCE
request = SearchRequest.model_validate(payload)

print(request.question)     # What was revenue? (trimmed)
print(request.top_k)        # 3 (access Python attribute, not alias)
print(request.start_year)   # 2024 (converted to int)
print(request.source.page)  # 3 (nested object access)
print(request.tags)         # [] (default_factory)
print(request.note)         # None (default)


# 2. DIRECT CONSTRUCTION ALSO VALIDATES
direct = SearchRequest(
    question="What was revenue?",
    start_year=2024,
    end_year=2025,
    source={"kind": "web", "url": "https://example.com/report"},
)

print(direct.top_k)       # 5 (default: topK was omitted)
print(direct.source.url)  # Nested object is a WebSource.


# 3. MODEL INSTANCE -> DICTIONARY
data = request.model_dump()

print(type(data))              # <class 'dict'>
print(data["source"]["page"])  # 3 (dictionary access now)
print(data["top_k"])           # Default export uses Python field names.

external_data = request.model_dump(by_alias=True)
print(external_data["topK"])   # by_alias=True exports the alias.


# 4. MODEL INSTANCE -> JSON STRING
text = request.model_dump_json(by_alias=True)

print(type(text))  # <class 'str'>
# JSON uses double quotes and null instead of Python's None.
# by_alias=True exports topK, matching this model's input alias.


# 5. JSON STRING -> VALIDATED MODEL INSTANCE
restored = SearchRequest.model_validate_json(text)

print(restored.source.page)  # 3 (object access again)


# Python-only conversions: these do NOT perform Pydantic validation.
plain_text = json.dumps(data)        # Dictionary -> JSON string.
plain_data = json.loads(plain_text)  # JSON object text -> dictionary.


# 6. CATCH VALIDATION ERRORS
bad_payload = {
    **payload,  # Copy payload, then override these fields.
    "question": "   ",  # Trims to empty -> min_length fails.
    "topK": "3",        # strict=True rejects a string.
    "source": {
        "kind": "file",
        "filename": "report.pdf",
        "page": 0,      # Violates ge=1.
    },
    "unexpected": True,  # Rejected by extra="forbid".
}

try:
    SearchRequest.model_validate(bad_payload)
except ValidationError as exc:
    for error in exc.errors():
        print(error["loc"], error["type"], error["msg"])
        # loc: failure path, e.g. ("source", "file", "page").
        # type: machine-readable error code.
        # msg: human-readable explanation.


# 7. CROSS-FIELD ERROR: demonstrate separately.
# The model after-validator runs only when field validation succeeds.
try:
    SearchRequest.model_validate({**payload, "end_year": 2023})
except ValidationError as exc:
    print(exc.errors()[0]["msg"])
    # Value error, end_year must be >= start_year.


# Pydantic validates structure and your rules—not factual truth.
```

## 1. Define, validate, and serialize a request

```python
from pydantic import BaseModel, ConfigDict, Field

class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str
    top_k: int = Field(default=5, ge=1, le=20)

request = SearchRequest.model_validate({"question": "What was revenue?"})
print(request.model_dump())
# {'question': 'What was revenue?', 'top_k': 5}


```

- Use `SearchRequest(question="What was revenue?")` when passing fields directly.
- Use `SearchRequest.model_validate(data)` when you already have a dictionary. Both forms validate the input.
- `extra="forbid"` rejects unexpected keys. Add `strict=True` to the integer field to reject `"3"` as input.
  
| Method | Input → Output |
|---|---|
| `SearchRequest.model_validate(data)` | Dictionary → model instance |
| `SearchRequest.model_validate_json(text)` | JSON string → model instance |
| `request.model_dump()` | Model instance → dictionary |
| `request.model_dump_json()` | Model instance → JSON string |

```python
data = {"active": True}       # Python dictionary

text = '{"active": true}'     # String containing valid JSON

bad = "{'active': True}"      # String, but NOT valid JSON
#use json.dumps to convert to json correctly
import json
text = json.dumps(data)  # '{"active": true}'

```



## 2. Clean a field before checking its constraints

```python
from pydantic import BaseModel, Field, field_validator

class SearchRequest(BaseModel):
    question: str = Field(min_length=1)

    @field_validator("question", mode="before")
    @classmethod
    def trim_question(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value
```

- `mode="before"` receives raw input. Trimming `"   "` first lets `min_length=1` reject the empty string.
- Use the default `after` mode when your function needs the already parsed value.
- Return the field value you want stored.

## 3. Validate a rule involving two fields

```python
from pydantic import BaseModel, model_validator

class ReportRequest(BaseModel):
    start_year: int
    end_year: int

    @model_validator(mode="after")
    def check_year_range(self):
        if self.end_year < self.start_year:
            raise ValueError("end_year must be >= start_year")
        return self
```

An `after` model validator receives `self` after the fields validate. Remember **`return self`** here. A field validator returns the field value.

## 4. Validate nested objects and give a list a default

```python
from pydantic import BaseModel, Field

class Source(BaseModel):
    filename: str
    page: int

class Answer(BaseModel):
    text: str
    sources: list[Source] = Field(default_factory=list)

answer = Answer.model_validate({
    "text": "Revenue grew by 12%.",
    "sources": [{"filename": "annual_report.pdf", "page": 3}],
})
print(answer.sources[0].page)  # 3
```

Each supplied source dictionary becomes a `Source`. When `sources` is omitted, Pydantic calls `list()` to create a fresh list. Pass `list` without parentheses.

## 5. Read structured validation errors

```python
from pydantic import BaseModel, Field, ValidationError

class SearchRequest(BaseModel):
    top_k: int = Field(ge=1, le=20)

try:
    SearchRequest.model_validate({"top_k": 0})
except ValidationError as exc:
    for error in exc.errors():
        print(error["loc"], error["type"], error["msg"])
```

- `loc` is the path to the failure. `("sources", 0, "page")` identifies `page` on the first source.
- `type` is the error code your program can check.
- `msg` is the readable explanation.

## 6. Map an external field name to a Python attribute

```python
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    top_k: int = Field(alias="topK")

request = SearchRequest.model_validate({"topK": 3})
print(request.top_k)                     # 3
print(request.model_dump(by_alias=True))  # {'topK': 3}
```

The payload uses `topK`. Python accesses `top_k`. Pass `by_alias=True` to export `topK`.

## 7. Select a payload shape using a discriminator

```python
from typing import Literal
from pydantic import BaseModel, Field

class FileSource(BaseModel):
    kind: Literal["file"]
    filename: str

class WebSource(BaseModel):
    kind: Literal["web"]
    url: str

class SearchRequest(BaseModel):
    source: FileSource | WebSource = Field(discriminator="kind")
```

Pydantic reads `source.kind` to choose the model. A source with `kind="file"` must provide `filename`. A source with `kind="web"` must provide `url`.

For recall practice, start from a requirement such as “reject a question containing only spaces” or “reject an end year earlier than the start year.” Choose the validator and write the snippet from memory.

# FastAPI + Requests: Must-Know Interview Snippets

Memorize the structure and understand each line.

```python
import httpx
import requests
from fastapi import FastAPI, Query, Path, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel, ConfigDict, Field
from requests.adapters import HTTPAdapter
from requests.exceptions import Timeout, ConnectionError, HTTPError, JSONDecodeError
from urllib3.util import Retry

app = FastAPI()  # ONE application; decorators register its endpoints.
BASE_URL = "http://127.0.0.1:8000"
companies = {42: "Acme"}


# SERVER: path parameters + a constrained query parameter.
@app.get("/companies/{company_id}/reports/{year}")
def get_report(
    company_id: int,
    year: int,
    top_k: int = Query(default=3, ge=1, le=10),
):
    # company_id/year come from the URL path; top_k comes after ?.
    # Example: /companies/42/reports/2024?top_k=5
    # FastAPI parses and validates BEFORE calling this handler.
    # Invalid int or out-of-range top_k -> HTTP 422.
    return {"company_id": company_id, "year": year, "top_k": top_k}
    # Returning a dictionary normally produces a JSON response with HTTP 200.


# SERVER: validated request body + a separate response contract.
class QuestionRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",              # Reject unexpected body fields.
        str_strip_whitespace=True,   # Trim strings before constraints.
    )
    question: str = Field(min_length=1, max_length=500)


class QuestionResponse(BaseModel):
    question: str


@app.post("/questions", response_model=QuestionResponse)
def ask_question(payload: QuestionRequest):
    # FastAPI validates the JSON body automatically.
    # No manual model_validate() call is needed.
    # Invalid request body -> 422.
    return {
        "question": payload.question,  # Access the model using a dot.
        "internal_note": "Do not expose",
    }
    # response_model validates/filters output: internal_note is excluded.
    # Missing/invalid required response fields -> server error (500).


# SERVER: input validation versus a meaningful application error.
@app.get("/companies/{company_id}")
def get_company(company_id: int = Path(gt=0)):
    if company_id not in companies:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    return {"company_id": company_id, "company": companies[company_id]}
    # 0 -> 422; 999 -> 404; 42 -> 200.
    # raise stops execution.
    # Returning an error dictionary alone would still default to 200.


# SERVER: dependency injection + bearer-token authentication.
bearer = HTTPBearer(auto_error=False)
# HTTPBearer extracts credentials; our function validates them.


def get_current_user(auth=Depends(bearer)):
    if auth is None or auth.credentials != "demo-token":
        # Short-circuiting avoids accessing .credentials on None.
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return "demo-user"  # Fixed token is only a learning example.


@app.get("/me")
def read_user(user=Depends(get_current_user)):
    # Pass the FUNCTION, not get_current_user().
    # FastAPI calls it and injects its returned value into user.
    return {"user": user}


# SERVER: call another HTTP endpoint from async code.
async def fetch_company(url):
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(url)
        # await allows other tasks to run during the network wait.

        response.raise_for_status()
        return response.json()  # No await: response body is already read.

    # async with closes the client.
    # For frequent calls, reuse an AsyncClient across requests.


@app.get("/companies/{company_id}/summary")
async def company_summary(company_id: int = Path(gt=0)):
    try:
        # This demo calls our existing company endpoint over HTTP.
        company = await fetch_company(
            f"{BASE_URL}/companies/{company_id}"
        )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, detail="Upstream timed out"
        )

    except httpx.HTTPStatusError as error:
        # Preserve the company's 404 rather than causing an unhandled 500.
        raise HTTPException(
            status_code=error.response.status_code,
            detail="Company lookup failed",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502, detail="Could not reach upstream"
        )

    return {"summary": f"Company: {company['company']}"}

    # Without await, fetch_company(...) only creates a coroutine object.
    # Blocking requests.get() directly inside async def blocks its event loop.


# CLIENT: run after starting the server in the other terminal.
def run_client():
    try:
        # GET: params= sends query parameters.
        response = requests.get(
            f"{BASE_URL}/companies/42/reports/2024",
            params={"top_k": 5},
            timeout=(2, 3),
        )
        # timeout=(connect, read), NOT a five-second overall deadline.

        response.raise_for_status()  # Check HTTP errors BEFORE parsing.
        data = response.json()       # This JSON object becomes a dict.
        print("GET:", data)

        # POST: json= accepts a Python dict and sends a JSON body.
        response = requests.post(
            f"{BASE_URL}/questions",
            json={"question": "What was revenue in 2024?"},
            timeout=5,
        )
        response.raise_for_status()
        print("POST:", response.json())  # internal_note is absent.

        # Authentication: token goes in the Authorization header.
        response = requests.get(
            f"{BASE_URL}/me",
            headers={"Authorization": "Bearer demo-token"},
            timeout=5,
        )
        response.raise_for_status()
        print("USER:", response.json())

        # A synchronous client can call an async server endpoint.
        response = requests.get(
            f"{BASE_URL}/companies/42/summary",
            timeout=10,
        )
        response.raise_for_status()
        print("SUMMARY:", response.json())

        # SESSION: reuse connections + configure bounded retries.
        retries = Retry(
            total=2,  # Initial attempt + up to 2 retries = 3 attempts.
            backoff_factor=0.5,
            status_forcelist=[429, 502, 503, 504],
            allowed_methods={"GET"},  # Restricts status/read retries.
            raise_on_status=False,   # Return the final HTTP response.
        )

        with requests.Session() as session:  # Keep OUTSIDE the loop.
            adapter = HTTPAdapter(max_retries=retries)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            for _ in range(3):  # Three fresh requests.
                response = session.get(
                    f"{BASE_URL}/companies/42",
                    timeout=(2, 3),
                )
                # Each request has its own retry cap.
                response.raise_for_status()  # Check final response.
                print("SESSION:", response.json())

        # Session closes automatically on exiting with.
        # Retry settings apply ONLY to calls through this session.
        # Session remains synchronous.
        # Retry counts do not bound total duration.
        # allowed_methods does not disable all connection retries for POST.
        # Before retrying POST, consider whether it already took effect.

        # Intentional failure LAST so earlier demonstrations complete.
        response = requests.get(
            f"{BASE_URL}/companies/999",
            timeout=(2, 3),
        )
        response.raise_for_status()  # Expected HTTPError: 404.

    except Timeout:
        # Catch before ConnectionError: ConnectTimeout inherits both.
        print("Timed out")

    except ConnectionError:
        print("Could not connect; check that the server is running")

    except HTTPError as error:
        print("HTTP error:", error.response.status_code)

    except JSONDecodeError:
        print("Response was not valid JSON")

    # Network, HTTP-status, and JSON-parsing failures are separate.
    # Successfully parsing JSON does NOT establish HTTP success.


if __name__ == "__main__":
    run_client()
    # Uvicorn imports app without running this client.
```

#### FastAPI under the hood:
## FastAPI: From Uvicorn Startup to Swagger UI

```bash
python -m uvicorn FastAPI_Interview_One_Example:app
```

1. **Python starts Uvicorn** — `-m uvicorn` runs the Uvicorn module.

2. **Uvicorn imports your file and selects `app`** — conceptually:
   ```python
   from FastAPI_Interview_One_Example import app
   ```

3. **Importing creates the application and registers routes** — `app = FastAPI()` creates the app; decorators such as `@app.get(...)` register handlers. Handler bodies do not run yet.

4. **The client is skipped** — importing sets `__name__` to `"FastAPI_Interview_One_Example"`, so the `if __name__ == "__main__":` block does not execute.

5. **Uvicorn starts listening** — defaults to `127.0.0.1:8000`. Keep the terminal running.

6. **Open [Swagger UI](http://127.0.0.1:8000/docs)** — the browser requests `/docs`, and FastAPI returns the Swagger UI page.

7. **Swagger loads `/openapi.json`** — FastAPI describes your endpoints, parameters, and models; Swagger renders that description as interactive documentation.

8. **Click “Try it out” → “Execute”** — Swagger sends a real API request. FastAPI validates the input, runs the selected handler, and returns the response.
9. 
Each server example is a separate `main.py`; run it with:

```bash
fastapi dev main.py
```

Client examples need the corresponding server running.

## 1. GET endpoint: path parameters + query parameters

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/companies/{company_id}/reports/{year}")
def get_report(
    company_id: int,
    year: int,
    top_k: int = Query(default=3, ge=1, le=10),
):
    return {
        "company_id": company_id,
        "year": year,
        "top_k": top_k,
    }
```

Example request:

```text
/companies/42/reports/2024?top_k=5
```

**Remember:**

- Placeholders in the route are path parameters.
- `top_k` is a query parameter with a default of `3`.
- `ge=1, le=10` means 1–10 inclusive.
- Invalid input produces `422`.

## 2. POST endpoint: validated body + response model

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)

class QuestionResponse(BaseModel):
    question: str

@app.post("/questions", response_model=QuestionResponse)
def ask_question(payload: QuestionRequest):
    return {
        "question": payload.question,
        "internal_note": "Do not expose",
    }
```

**Remember:**

- `payload: QuestionRequest` validates the incoming JSON body.
- Access fields using `payload.question`.
- `response_model` validates and filters outgoing data: `internal_note` is excluded.
- Invalid request → `422`.
- Invalid data returned by your handler → server error.

## 3. Raise a meaningful API error

```python
from fastapi import FastAPI, HTTPException, Path

app = FastAPI()
companies = {42: "Acme"}

@app.get("/companies/{company_id}")
def get_company(company_id: int = Path(gt=0)):
    if company_id not in companies:
        raise HTTPException(
            status_code=404,
            detail="Company not found",
        )

    return {"company": companies[company_id]}
```

**Remember:**

- `raise HTTPException(...)` stops execution.
- `0` fails input validation → `422`.
- `999` passes validation but fails the company lookup → `404`.
- Returning an error dictionary alone would still use the default `200`.

## 4. Call an API: request → status check → JSON

### GET with query parameters

Targets the endpoint in example 1.

```python
import requests

response = requests.get(
    "http://127.0.0.1:8000/companies/42/reports/2024",
    params={"top_k": 5},
    timeout=5,
)

response.raise_for_status()
data = response.json()
print(data)
```

### POST with a JSON body

Targets the endpoint in example 2.

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/questions",
    json={"question": "What was revenue in 2024?"},
    timeout=5,
)

response.raise_for_status()
data = response.json()
print(data)
```

**Remember:**

- `params=` sends query parameters.
- `json=` sends a JSON body.
- Set a timeout.
- Check HTTP status before parsing the response.
- Successfully parsing JSON does not prove the HTTP request succeeded.

## 5. Handle client failures separately

```python
import requests
from requests.exceptions import (
    Timeout, ConnectionError, HTTPError, JSONDecodeError,
)

try:
    response = requests.get(
        "http://127.0.0.1:8000/companies/42",
        timeout=(2, 3),
    )
    response.raise_for_status()
    print(response.json())

except Timeout:
    print("Timed out")

except ConnectionError:
    print("Could not connect")

except HTTPError as error:
    print("HTTP error:", error.response.status_code)

except JSONDecodeError:
    print("Response was not valid JSON")
```

**Remember:**

- Network failure, HTTP failure, and JSON parsing failure are separate problems.
- `timeout=(2, 3)` specifies connection/read timeouts.
- It is not a five-second overall deadline.
- `error.response.status_code` gives the status associated with an `HTTPError`.

## 6. Depends + bearer-token authentication

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer

app = FastAPI()
bearer = HTTPBearer(auto_error=False)

def get_current_user(auth=Depends(bearer)):
    if auth is None or auth.credentials != "demo-token":
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return "demo-user"

@app.get("/me")
def read_user(user=Depends(get_current_user)):
    return {"user": user}
```

The caller sends `headers={"Authorization": "Bearer demo-token"}` in its Requests call.

**Remember:**

- `Depends(get_current_user)` passes the function to FastAPI.
- FastAPI calls it and injects its returned value into `user`.
- Do not write `Depends(get_current_user())`.
- Check `auth is None` before accessing `auth.credentials`.
- The fixed token is a learning example.
- `HTTPBearer` extracts credentials; your authentication logic must validate them.

## 7. Call another API from async code

```python
import httpx

async def fetch_company(url):
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

**Remember:**

- Inside an async endpoint, use `company = await fetch_company(url)`.
- `async with` manages the client's lifetime.
- `await client.get(...)` allows other tasks to run during network waits.
- This function resumes after the response is available.
- `.json()` needs no `await` because the response body is already loaded.
- Calling `fetch_company(url)` without awaiting or scheduling it only creates a coroutine object.
- Calling blocking `requests.get()` directly inside `async def` blocks the event-loop thread.

## 8. Reuse a Session + configure bounded retries

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

retries = Retry(
    total=2,
    backoff_factor=0.5,
    status_forcelist=[429, 502, 503, 504],
    allowed_methods={"GET"},
    raise_on_status=False,
)

with requests.Session() as session:
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    for _ in range(3):
        response = session.get(
            "http://127.0.0.1:8000/companies/42",
            timeout=(2, 3),
        )
        response.raise_for_status()
        print(response.json())
```

**Remember:**

- Keep the Session outside the loop to reuse connections.
- Each loop iteration makes a fresh request.
- A Session does not make Requests asynchronous.
- `total=2` permits up to two retries per request: three attempts.
- `allowed_methods` restricts status/read retries; connection-error retries have separate semantics.
- `raise_on_status=False` returns the final HTTP response after status retries are exhausted.
- `response.raise_for_status()` then checks that final response.
- Before retrying a POST, consider whether the first attempt already created something.

## Practice priority

Write **1–7 from a blank file** until they feel familiar.

For **8**, understand the settings and recognize the adapter recipe. The particular retry counts and delays depend on the application.

# MCP — Must-Memorize FDE Interview Notes
```python
import asyncio
from mcp import Client
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

server = MCPServer("finance")


@server.tool()
def get_revenue(company: str, year: int) -> dict[str, int]:
    """Get annual revenue in USD."""
    data = {("ACME", 2024): 100000}
    key = (company, year)

    if key not in data:
        raise ToolError("Revenue unavailable for that company/year")

    return {"revenue": data[key]}


@server.resource("reports://annual/{company}/{year}")
def report(company: str, year: str):
    return f"{company} {year}: revenue grew 12%"


@server.prompt()
def review_report(company: str):
    """Build an instruction to review a company's report."""
    return f"Review {company}'s report. Cite evidence for each risk."


async def main():
    async with Client(server) as client:
        # Discover tools.
        listed = await client.list_tools()
        tool = listed.tools[0]
        print(tool.name, tool.input_schema["required"])
        # get_revenue ['company', 'year']

        # Successful tool call.
        result = await client.call_tool(
            "get_revenue", {"company": "ACME", "year": 2024}
        )
        print(result.is_error)             # False
        print(result.structured_content)   # {'revenue': 100000}

        # Business-rule failure.
        result_2 = await client.call_tool(
            "get_revenue", {"company": "ACME", "year": 2025}
        )
        print(result_2.is_error)            # True
        print(result_2.content[0].text)

        # Input-validation failure.
        invalid = await client.call_tool(
            "get_revenue", {"company": "ACME", "year": "abc"}
        )
        print(invalid.is_error)             # True

        # Discover and read a resource.
        templates = await client.list_resource_templates()
        print(templates.resource_templates[0].uri_template)
        # reports://annual/{company}/{year}

        result_3 = await client.read_resource(
            "reports://annual/ACME/2025"
        )
        print(result_3.contents[0].text)
        # ACME 2025: revenue grew 12%

        # Discover and retrieve a prompt.
        listed_prompts = await client.list_prompts()
        print([prompt.name for prompt in listed_prompts.prompts])
        # ['review_report']

        result_4 = await client.get_prompt(
            "review_report", {"company": "ACME"}
        )
        message = result_4.messages[0]
        print(message.role)                # user
        print(message.content.text)
        # Review ACME's report. Cite evidence for each risk.


asyncio.run(main())
```

**Version:** official Python SDK `mcp==2.3.0`, Python 3.11+. These examples use `MCPServer` and `Client`. Older official SDK v1 examples use different imports, such as `mcp.server.fastmcp.FastMCP`; do not mix their APIs with these examples.

```bash
python -m pip install "mcp[cli]==2.3.0"
```

Each Python example is a complete file. Examples 1–4 and 7 connect the client and server in the same process so you can run them directly. Examples 5–6 demonstrate actual process/network connections. No LLM, API key, or external financial service is used; the revenue data is simulated.

## 0. What MCP does

MCP gives an AI application a standard way to discover and call tools, read data, and retrieve reusable prompts. In your CAR application, it could expose `search_index` and `sql` to different compatible agent applications.

| Component | Job |
| --- | --- |
| Host | Your AI application: manages the model, conversation, and permission decisions. |
| Client | The part of the host that communicates with an MCP server. |
| Server | Exposes tools, resources, and prompts; implements the underlying operations. |

| Primitive | Purpose | CAR example | Typically selected by |
| --- | --- | --- | --- |
| Tool | Execute an operation; it may read or change data. | Search the evidence index. | Model, under host controls. |
| Resource | Read data identified by a URI. | Load a report section. | Application. |
| Prompt | Retrieve a reusable message template. | Build a credit-review instruction. | User. |

**Critical notes:**

- MCP supplies the connection and contracts. Your agent still decides which tools to call and how to use their results.
- A client can call a tool directly, as the examples do; an LLM is not required.
- LangGraph controls workflow and state. MCP can provide tools used by that workflow. MCP does not replace graph checkpointing or approval logic.

## 1. Register, discover, and call a tool

```python
import asyncio
from mcp import Client
from mcp.server import MCPServer

server = MCPServer("Finance")

@server.tool()
def get_revenue(company: str, year: int) -> dict[str, int]:
    """Get annual revenue in USD for a company."""
    data = {("Acme", 2025): 120_000_000}
    return {"revenue": data[(company, year)]}

async def main():
    async with Client(server) as client:
        listed = await client.list_tools()
        tool = listed.tools[0]
        print(tool.name, tool.input_schema["required"])
        # get_revenue ['company', 'year']

        result = await client.call_tool(
            "get_revenue", {"company": "Acme", "year": 2025}
        )
        print(result.is_error)            # False
        print(result.structured_content)  # {'revenue': 120000000}

asyncio.run(main())
```

**Critical notes:**

- `@server.tool()` registers the function. Its name, docstring, and parameter annotations define the tool's discoverable contract.
- Keep these annotations: input types build the input schema; the return type here enables structured output.
- `list_tools()` discovers definitions; `call_tool()` executes one with an argument dictionary.
- Check `is_error` before consuming results. `structured_content` is machine-readable data; `content` holds text/media blocks and is not always one string.
- `Client(server)` is an in-process connection for local practice; it does not exercise HTTP authentication. `async with` manages its lifecycle, and the client handles protocol negotiation.

## 2. Handle tool failures and invalid arguments

```python
import asyncio
from mcp import Client
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

server = MCPServer("Finance")

@server.tool()
def get_revenue(year: int) -> dict[str, int]:
    """Get Acme's annual revenue in USD."""
    if year != 2025:
        raise ToolError("Revenue unavailable for that year")
    return {"revenue": 120_000_000}

async def main():
    async with Client(server) as client:
        result = await client.call_tool("get_revenue", {"year": 2024})
        print(result.is_error)  # True
        print(result.content[0].text)
        # Error executing tool get_revenue: Revenue unavailable for that year

        invalid = await client.call_tool("get_revenue", {"year": "abc"})
        print(invalid.is_error)  # True: input validation rejects "abc".

asyncio.run(main())
```

**Critical notes:**

- An expected tool failure can return `is_error=True` without raising an exception in the client.
- Returning `"Error: ..."` as an ordinary string does not mark the call as failed. Use the SDK's error mechanism.
- Schema validation checks input shape/types; your function still enforces business rules.
- A protocol error or connection failure is a separate failure path and may raise in the client. Do not treat every failure as a successful tool response.

## 3. Expose and read a resource

```python
import asyncio
from mcp import Client
from mcp.server import MCPServer

server = MCPServer("Reports")

@server.resource("reports://annual/{company}/{year}")
def report(company: str, year: str):
    return f"{company} {year}: revenue grew 12%."

async def main():
    async with Client(server) as client:
        templates = await client.list_resource_templates()
        print(templates.resource_templates[0].uri_template)
        # reports://annual/{company}/{year}

        result = await client.read_resource("reports://annual/Acme/2025")
        print(result.contents[0].text)
        # Acme 2025: revenue grew 12%.

asyncio.run(main())
```

**Critical notes:**

- A resource is read by URI. Its URI can contain parameters that the SDK passes to your function.
- `list_resources()` lists fixed resources; `list_resource_templates()` lists parameterized templates.
- Reading a resource does not automatically add it to the model's conversation; the host decides how to use the returned data.
- This resource returns text. Other resources can return binary content, so inspect the content type when writing a generic client.

## 4. Expose and retrieve a prompt

```python
import asyncio
from mcp import Client
from mcp.server import MCPServer

server = MCPServer("ReviewPrompts")

@server.prompt()
def review_report(company: str):
    """Build an instruction for reviewing a company's report."""
    return f"Review {company}'s report. Cite evidence for each risk."

async def main():
    async with Client(server) as client:
        listed = await client.list_prompts()
        print([prompt.name for prompt in listed.prompts])
        # ['review_report']

        result = await client.get_prompt("review_report", {"company": "Acme"})
        message = result.messages[0]
        print(message.role)          # user
        print(message.content.text)
        # Review Acme's report. Cite evidence for each risk.

asyncio.run(main())
```

**Critical notes:**

- `get_prompt()` returns rendered messages. It does not run an LLM or produce the report review.
- Prompt arguments are strings. Tool arguments can use the types declared by the tool's schema.
- This SDK turns a prompt's returned string into a user-role prompt message. The host adapts it to the model interface it uses.

## 5. Connect to a local server over stdio

Save this complete example as `mcp_stdio.py` and run `python mcp_stdio.py`. The client launches another copy of this file in server mode.

```python
import asyncio
import sys
from pathlib import Path
from mcp import Client, StdioServerParameters
from mcp.server import MCPServer

server = MCPServer("Calculator")

@server.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

async def main():
    process = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).resolve()), "--server"]
    )
    async with Client(process) as client:
        result = await client.call_tool("add", {"a": 2, "b": 3})
        print(result.structured_content)  # {'result': 5}

if __name__ == "__main__":
    if "--server" in sys.argv:
        server.run()  # stdio server; waits for MCP requests.
    else:
        asyncio.run(main())
```

**Critical notes:**

- stdio connects a client to a local subprocess through stdin/stdout; no HTTP port is involved.
- The client context starts and cleans up the subprocess. `--server` is our own flag to choose which mode this file runs in.
- Keep server diagnostic logs on stderr; stdout is used for protocol traffic. The `print()` above runs in the client process.
- The SDK wraps a scalar structured result as `{"result": value}`.
- Pass required credentials explicitly through the subprocess configuration; do not assume it inherits every environment variable.

## 6. Serve and call MCP over HTTP

Save this complete example as `mcp_http.py`. In terminal 1 run `python mcp_http.py --server`; in terminal 2 run `python mcp_http.py`.

```python
import asyncio
import sys
from mcp import Client
from mcp.server import MCPServer

server = MCPServer("Calculator")

@server.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

async def main():
    async with Client("http://127.0.0.1:8000/mcp") as client:
        result = await client.call_tool("add", {"a": 2, "b": 3})
        print(result.structured_content)  # {'result': 5}

if __name__ == "__main__":
    if "--server" in sys.argv:
        server.run(transport="streamable-http", port=8000)
    else:
        asyncio.run(main())
```

**Critical notes:**

- Use Streamable HTTP for network-accessible MCP servers; stdio is for local subprocesses.
- `/mcp` is the SDK's default MCP endpoint. It carries protocol requests; there is no separate `/add` route in this example.
- Transport options such as `port` belong to `run()` in this SDK version.
- These localhost examples do not implement authentication or business authorization. Deployment requires those separately.

## 7. Bound how long the client waits

```python
import asyncio
from mcp import Client
from mcp.server import MCPServer

server = MCPServer("SlowDemo")

@server.tool()
async def slow_lookup(company: str) -> str:
    """Simulate a slow company lookup."""
    await asyncio.sleep(2)
    return company

async def main():
    async with Client(server) as client:
        try:
            async with asyncio.timeout(0.1):
                await client.call_tool("slow_lookup", {"company": "Acme"})
        except TimeoutError:
            print("Tool call timed out")  # Tool call timed out

asyncio.run(main())
```

**Critical notes:**

- This sets a deadline for the awaited call. Configure timeouts on any upstream API calls inside tools as well.
- A timeout does not prove a remote operation never happened. Retrying a write requires an idempotency strategy.
- These examples are ordinary Python scripts. In a notebook with an active event loop, replace the final `asyncio.run(main())` with `await main()`.

## Interview points to explain without code

| Question | Answer to defend |
| --- | --- |
| Why MCP instead of a Python function? | It supplies a standard discovery and invocation interface that different compatible applications can use. It is useful at an integration boundary; a local function may be sufficient within one program. |
| Does MCP choose the tool? | The host/model or application code chooses; the MCP client sends the call and the server executes it. |
| Does exposing a tool authorize every user? | No. Authenticate callers and enforce user/tenant permissions on the server for the requested operation. |
| Where does approval belong? | The host's workflow can request approval before a sensitive call; server authorization is still enforced. A tool description is not an access-control rule. |
| Can a timeout cause duplicate writes? | Yes, if a completed operation is retried. Use idempotency keys or an equivalent deduplication mechanism for writes. |
| Can tool output contain hostile instructions? | Yes. Treat returned content as external data; it must not grant itself permissions or override the application's rules. |
| How do you debug an MCP integration? | First discover and call the tool directly, inspect the input schema and error result, then examine transport/server logs. Add the model after the tool path works. |

For a visual debugging client, save example 5 as `mcp_stdio.py` and run `mcp dev mcp_stdio.py` with Node.js/npm available. It opens the MCP Inspector; the server object is already defined in that file.

## Sources and validation

Examples were executed with the official Python SDK `mcp==2.3.0`. Expected comments describe explicit program output; server diagnostics may also appear on stderr.

| Code | What it does |
|---|---|
| `async def work(): ...` | **Defines** an async function; its body does not run |
| `job = work()` | **Creates a coroutine object**; its body still does not run |
| `result = await job` | **Executes that coroutine** and waits for its result |
| `async with resource:` | Automatically awaits the resource’s setup and cleanup |
| `asyncio.run(main())` | Starts an event loop and runs the outer coroutine |

| Connection style | Client setup | Where the server runs |
|---|---|---|
| **In-process** | `Client(server)` | Inside the same Python process. No separate process or HTTP port. Useful for practice/testing. |
| **stdio** | `Client(process)` | The client launches a local subprocess and communicates through its stdin/stdout. |
| **Streamable HTTP** | `Client("http://127.0.0.1:8000/mcp")` | Connects to an already-running HTTP server, locally or remotely. |
