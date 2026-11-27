# MCQ review

## MCP

- The **Model Context Protocol (MCP)** gives LLM applications a standard way to read data and call tools in external systems. Multiple applications can reuse the same server integration.

### Resources and tools

- **Read a resource by URI.** Calling `resources/read` with `policy://payments/limits` retrieves the current payment limits. The client has read-only access to the resource, even as the underlying policy changes.
- **Discover tools at runtime.** `tools/list` returns the names, descriptions, and input schemas of the tools the server currently offers. The list can change as the server adds or removes tools.
- **Call a tool by name.** A tool’s `inputSchema` uses JSON Schema to describe its arguments. For example, `get_spending` might require an `account_id` of type `string`. The same function can return a different total after a transaction posts.
- **Function calling is optional.** A model can request a tool and supply its arguments. The app’s MCP client sends `tools/call`, the server runs the tool, and the app can pass the result back to the model. The tool can be written in Python or another language.
- **Safety hints describe expected behavior.** With `readOnlyHint: true`, a tool declares that it only reads data. The server still has to enforce permissions and prevent unauthorized writes.

### Running async code from a Click command

- Keep the Click command synchronous. In `greet()`, `asyncio.run(_greet())` runs the coroutine to completion and returns its result. The leading underscore marks an internal helper by convention.
- In this small example, `_greet()` returns a greeting. In an MCP client, the helper can also use `await` to retrieve a prompt.

```python
import asyncio
import click

@click.command()
def greet():
    click.echo(asyncio.run(_greet()))

async def _greet():
    return "Hello!"

if __name__ == "__main__":
    greet()
```

### Retrieving an MCP prompt

- On an initialized `ClientSession`, call `await session.get_prompt(name)` with the server’s registered prompt name. If the prompt requires inputs, pass them in `arguments`.
- Loop over `result.messages` in order. Each message pairs a role such as `"user"` or `"assistant"` with its content. For text content, `message.content.text` gives you the string to print.

```python
async def print_prompt(session, name):
    result = await session.get_prompt(name)
    for message in result.messages:
        content = message.content
        if content.type == "text":
            print(message.role, content.text)
        else:
            print(message.role, content)
```

### Reading an MCP resource

- On an initialized `ClientSession`, the Python SDK v1 example passes a Pydantic `AnyUrl` to `read_resource()`. Wrap the resource’s URI string with `AnyUrl(uri)` before the call. A normal installation of `mcp` includes Pydantic as a dependency.
- **Read a resource by URI** and use `result.contents` for its data. **Retrieve a prompt by name** and use `result.messages` for its role-tagged messages.

```python
from pydantic import AnyUrl

async def read_payment_limits(session):
    uri = "policy://payments/limits"  # Example URI exposed by the server
    result = await session.read_resource(AnyUrl(uri))
    return result.contents
```

### Calling an MCP tool from the CLI

- The CLI receives the tool’s arguments as one JSON string, such as `'{"customer_name": "Alice"}'`. For a JSON object, `json.loads(arguments)` returns a Python dictionary that you can pass to `session.call_tool()` with the tool name.
- This example assumes the keys and values match the tool’s `inputSchema`. Parsing checks JSON syntax. Schema validation is a separate step.

```python
import json

async def call_from_cli(session, tool_name, arguments):
    tool_args = json.loads(arguments)
    return await session.call_tool(tool_name, arguments=tool_args)
```

### Cursor and server registration

- **Cursor is the host.** It’s a code editor with an AI assistant. Its MCP client connects to a server and makes the server’s tools available to the model.
- **Register a local server with a name and launch command.** In the project’s `.cursor/mcp.json`, `spending` is the name shown in Cursor, `command` selects the Python executable, and `args` passes the server script. If you installed the SDK in a virtual environment, point `command` to that environment’s Python executable.

  ```json
  {
    "mcpServers": {
      "spending": {
        "type": "stdio",
        "command": "python",
        "args": ["${workspaceFolder}/server.py"]
      }
    }
  }
  ```

- **Register a remote server with a name and endpoint URL.** The server is already running. Supply authentication details if it requires them.

### Launching a local server with uv

- **Cursor starts the conversation.** Its MCP client can launch a local server and ask it to run `get_spending`. The server can call the spending API to answer. It can also send supported notifications to a connected client, such as an update when its tool list changes.
- **“From anywhere” means from any folder on the same computer.** Cursor can already launch the server with Python and the script’s path. Installing the project with uv is an optional way to give that server a short launch command.
- **Run `uv tool install -e .` once from the project folder** (the one containing `pyproject.toml`). The dot means “this folder.” If the project defines a command called `spending-server`, uv installs that command for your user. With uv’s executable directory on Cursor’s `PATH`, Cursor can use `"command": "spending-server"` to launch it. Here, the uv tool is the server program. `get_spending` is an MCP tool that program exposes.
- **`-e` means editable.** The installation uses the Python files in your project folder. If you edit `get_spending()`, save the file and restart the server. The new process uses your edit without another install.

### Local stdio transport

- **One client per server process.** With `mcp.run(transport="stdio")`, the client launches the server and communicates through standard input and output. A second client typically starts a separate process.
- **Client authentication.** The stdio transport has no built-in client authentication. The local connection relies on operating-system permissions. A server calling an external API can still load that API’s credentials from an environment variable.

### MCP client · Managing a stdio connection

- The **stdio transport** starts the local server process and opens the streams used to send requests and read replies. The **client session** uses those streams to send MCP requests such as “list the tools.”

```python
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def get_tool_names(server_params):
    # server_params specifies the command that starts your MCP server.
    async with AsyncExitStack() as stack:
        read, write = await stack.enter_async_context(stdio_client(server_params))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()  # Client and server perform the MCP handshake.
        result = await session.list_tools()
        return [tool.name for tool in result.tools]
```

- **Open the transport, then the session.** `stdio_client(server_params)` provides the `read` and `write` streams. `ClientSession(read, write)` uses those streams to send MCP requests. Each is a separate asynchronous context manager.
- **Register both on one stack.** `AsyncExitStack` is a helper from Python’s `contextlib`. Each `await stack.enter_async_context(...)` enters the context manager, returns its entry value, and registers its `__aexit__()` for cleanup. [Real Python on contextlib](https://realpython.com/ref/stdlib/contextlib/)
- **Clean up in reverse order.** Leaving `async with AsyncExitStack()` runs the stack’s `__aexit__()`. It closes the session first, while its streams are still open, then closes the transport. This also happens on an early return or if `session.initialize()` raises an exception.

- A timeout controls how long a request waits. A lock controls who can access a resource. The context managers handle releasing it.

#### Asynchronous context managers

- **On entry**, `async with manager as value` awaits `manager.__aenter__()`. This runs setup, such as opening a connection. Python assigns the return value to `value`.
- **On exit**, after entry succeeds, Python awaits `manager.__aexit__(exc_type, exc, tb)` for cleanup. This also happens if the block returns early or raises an exception.
- **In a class**, the usual definitions are `async def __aenter__(self)` and `async def __aexit__(self, exc_type, exc, tb)`. A synchronous `with` block uses `__enter__()` and `__exit__()`. [Real Python glossary](https://realpython.com/ref/glossary/asynchronous-context-manager/)

```python
async def list_tools(read, write):
    async with ClientSession(read, write) as session:  # __aenter__ supplies session
        await session.initialize()
        return await session.list_tools()  # __aexit__ runs before the caller gets the result
```

### Building, testing, and hosting

- **Build in Python.** Install the official SDK with `python -m pip install mcp`. Register a function with `@mcp.tool()`. The SDK handles protocol messages and can derive the input schema from Python type hints.
- **Test with an MCP client.** Cursor can call a tool on behalf of a model. For a manual test without an LLM, use **MCP Inspector** to select the tool, enter arguments, and inspect the result.
- **Host on Azure.** Start with the Azure Functions Python MCP tools template, expose your function with `@app.mcp_tool_trigger(...)`, deploy with `azd up`, and register the Function App’s `/runtime/webhooks/mcp` URL in your client. [Azure walkthrough](https://learn.microsoft.com/en-us/azure/foundry/mcp/build-your-own-mcp-server)

### MCP and REST

- **REST exposes HTTP routes.** A spending API might document its routes with OpenAPI. To read October’s total, the client sends `GET /accounts/42/spending?month=2026-10`.
- **MCP exposes tools a client can discover and call.** For the same lookup, the client discovers `get_spending` with `tools/list`, then sends `tools/call` with the tool name and arguments `{"account_id":"42","month":"2026-10"}`.
- **Both can use the same spending calculation.** The MCP tool can call the existing REST endpoint and return its result.

## Quick reference notes

### Graph databases

**Nodes** represent entities, **relationships** connect them, and **properties** store details about either. In “Dr. Rao has worked at Oak Hospital since 2022,” the doctor and hospital are nodes, their names are node properties, and `WORKS_AT` is the relationship. The property `start_year = 2022` belongs to that relationship because it describes this particular job. [Real Python overview](https://realpython.com/build-llm-rag-chatbot-with-langchain/#a-brief-overview-of-graph-databases)

### FastAPI · Declaring GET and POST endpoints

**Common REST operations.** Use `POST` to create a resource, `GET` to read it, `PUT` to replace it in full, and `DELETE` to remove it.

**Quiz answer — `@api.post("/reviews")` registers a POST endpoint when the application is named `api`.** The decorator goes directly above the function that handles the request. If you wrote `app = FastAPI()`, use `@app.post(...)` and `@app.get(...)` instead.

```python
from fastapi import FastAPI
from pydantic import BaseModel

api = FastAPI()

class Review(BaseModel):
    text: str

@api.get("/health")
def get_health():
    return {"status": "ok"}

@api.post("/reviews")
def count_review_words(review: Review):
    return {"word_count": len(review.text.split())}
```

| Request | What the handler does |
|---|---|
| `GET /health` | Reads the service status and returns `{"status": "ok"}`. |
| `POST /reviews` with JSON body `{"text": "Friendly nurses"}` | FastAPI validates the body as a `Review`. The handler returns `{"word_count": 2}`. |

#### POST decorators in FastAPI and Azure Functions

**Which decorator handles an incoming chat request?** Check how `app` was created.

| Framework | Application object | POST decorator |
|---|---|---|
| FastAPI | `app = FastAPI()` | `@app.post("/chat")` |
| Azure Functions | `app = func.FunctionApp()` | `@app.route(route="chat", methods=["POST"])` |

In FastAPI, `.post` selects the method and `"/chat"` gives the path. In Azure Functions, `route="chat"` sets the route and `methods=["POST"]` selects the method. That is why the quiz choice `@app.route('POST')` is wrong: it puts `'POST'` in the route argument.

#### Swagger UI and tag groups

**1. Testing in `/docs`.** FastAPI serves Swagger UI at `/docs` by default. Expand an endpoint and select **Try it out → Execute** to send a real request. When the page is at `http://localhost:8000/docs` and calls `http://localhost:8000/reviews`, both have the same protocol, host, and port. A separate browser frontend on port `3000` is a different origin, so the API must permit that origin through CORS for its JavaScript to read the response.

**2. Grouping an endpoint.** Think of a tag as a section heading in Swagger UI. Use `openapi_tags` on the app to describe a group. Then put its exact name in the route decorator’s `tags=[...]` list.

```python
from fastapi import FastAPI

api = FastAPI(openapi_tags=[
    {"name": "Reviews", "description": "Patient review endpoints."}
])

@api.get("/reviews", tags=["Reviews"])
def list_reviews():
    return []
```

**Interview recall.** Read the decorator as “Clients call `GET /reviews` and developers find it under **Reviews** in `/docs`.” The URL path and the docs heading have separate jobs. The spelling and capitalization in `tags=["Reviews"]` match the predefined group name.

#### Request validation and HTTP 422

For `POST /hospitals/42/reviews?publish=false` with JSON body `{"rating": 5}`, the **path** supplies `hospital_id=42`, the **query** supplies `publish=False`, and a **Pydantic body model** validates `rating`. Query parameters bind by name in any order.

**422 rule:** If the route matches but a required input is missing or a supplied value fails validation, FastAPI returns **422** before your handler runs. Assume `hospital_id: int`, `publish: bool = True`, and a required body with `rating: int`.

| What you send | Result |
|---|---|
| Omit `publish`, or send just `?false` | With a valid path and body, the request succeeds. The name `publish` is absent, so its default is `True`. |
| `?publish=false` / `?publish=maybe` | `false` parses as `False`. `maybe` fails boolean validation → **422**. |
| `/hospitals/abc/reviews` | `abc` cannot be parsed as an integer → **422**. |
| No body, `{}`, or `{"rating": "great"}` | The required body or field is missing, or the rating cannot be parsed as an integer → **422**. |

If a route instead requires **two named query parameters** (`publish: bool, limit: int`), `?limit=10&publish=false` works. Sending `?publish=false` misses `limit` → **422**. Sending `?false&10` misses both names → **422**.

A URL matching no route returns **404**. For a **422**, look at `detail[].loc` in the response: for example, `["body", "rating"]` identifies the failing field.

#### Query validation with `Annotated` and `Query`

```python
from typing import Annotated
from fastapi import FastAPI, Query

api = FastAPI()

@api.get("/reviews")
def get_reviews(
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum reviews to return")] = 10,
):
    return {"limit": limit}
```

Read `limit` in three pieces. **`int`** gives the type. **`Query(...)`** sets the inclusive range of 1–100 and adds help text to the API docs. **`= 10`** supplies the default when the caller omits the parameter.

| Request | Result |
|---|---|
| `GET /reviews` | `200` with `{"limit": 10}` — default used. |
| `GET /reviews?limit=5` | `200` with `{"limit": 5}` — valid integer in range. |
| `GET /reviews?limit=101` | `422` — integer exceeds the maximum. |
| `GET /reviews?limit=abc` | `422` — value cannot be parsed as an integer. |

**JSON responses.** When a route returns a Python dictionary such as `{"message": "Hello, FastAPI!"}`, FastAPI automatically serializes it to JSON and sends it with the `application/json` content type by default.

**Automatic request tracing.** With the FastAPI instrumentation package installed, prefix your server command with `opentelemetry-instrument` (for example, `opentelemetry-instrument uvicorn main:api` when `main.py` defines `api = FastAPI()`). OpenTelemetry can then record how long a request such as `POST /reviews` took and which HTTP status it returned, without adding tracing code to your route handlers.

**Trace sampling (`traceidratio`).** A trace follows one request through the app. The sampler uses the trace ID to decide whether to record that trace for export. Set these environment variables before starting the app:

```bash
export OTEL_TRACES_SAMPLER=traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.10
```

The first setting selects the sampler. The second sets the fraction: `0` samples none, `0.10` samples about 10%, and `1` samples all. If 1,000 requests each start a new trace, expect roughly 100 sampled traces. The exact count varies. All 1,000 requests still run.

**Why use it in production?** Sampling reduces the trace data you send and store. For a sampled slow chatbot request, a trace with retrieval and LLM spans shows how much time each step took. Because the sampler decides at the start, a rare request that later fails may have no saved trace.

**If the failure was missed:** Other traces can reveal a recurring bottleneck, but they cannot reconstruct one particular request. At a 10% head-sampling rate, a one-off failure has only about a 1-in-10 chance of being traced. Look for any error logs recorded independently for that request. Sampling is optional: if volume and cost allow, retain all traces. At higher volume, a tail sampler can keep traces with recorded errors or high latency and a fraction of ordinary successes. It can only keep traces that reach it.

**Recall:** Read `@api.post("/reviews")` as “on this app, send POST requests for this path to the function below.”

---

Questions 1, 3, 6a, 8a, 15, and 16 are from the quiz. The other questions cover the follow-ups we discussed.

## LangGraph · Installing the Python library

### 1. After installing LangGraph with `pip`, what’s a good approach to verifying that the installation was successful?

**Correct choice — Start a Python REPL and import `langgraph` without errors.**

**Why** — Look at the first word of each command. It tells you what you’re running.

| What you type | Where you type it | What happens |
|---|---|---|
| `pip install langgraph` | Terminal | The terminal starts **pip**. Pip installs the Python library. |
| `import langgraph` | Python prompt (`>>>`) | **Python** loads the library. If the prompt comes back without an error, the import worked. |
| `langgraph --version` | Terminal | The terminal looks for a **program named langgraph**. That command comes from a separate package, `langgraph-cli`. |

### 2. Which package do I need for my Python orchestration code?

**Answer — `pip install langgraph`.**

**Why** — This provides `from langgraph.graph import StateGraph`, the class you use to connect nodes and compile a graph. The optional CLI is for terminal commands such as `langgraph dev`, which starts a local development server.

## Pydantic AI · Getting a structured answer

### 3. When you give an agent a Pydantic model as `output_type`, which of the following behaviors do you get?

**Correct choices — Select 1, 3, and 4.**

| Quiz choice | Why it’s correct |
|---|---|
| **1. Validate the output and retry on failure.** | If `rating` must be an integer and the LLM returns `"great"`, the agent asks the LLM to correct it, up to the retry limit. |
| **3. Return a validated model instance in `result.output`.** | If the LLM returns a valid rating of 4, you can read `result.output.rating` directly and get the integer `4`. The framework handles the parsing. |
| **4. Generate a JSON schema.** | Before the LLM answers, the agent turns your field definition, such as `rating: int`, into a description of what the answer must contain. |

### 4. When validation fails, what runs again?

**Answer — The agent calls the LLM again and checks its new answer.**

**Why** — You call `agent.run_sync(...)` once. Inside that run, the LLM might first return `{"rating": "great"}`. The agent sends back the validation error. If the LLM then returns `{"rating": 4}`, validation passes and the run ends.

### 5. If I allow two output retries, how many attempts can the LLM make?

**Answer — Up to three attempts for this rating: one initial answer plus two retries.**

**Why** — In `Agent(model, output_type=Review, retries={"output": 2})`, the `2` counts *extra* attempts. A valid first answer takes one call. If the third answer still fails validation, the run raises an error.

## ChatPromptTemplate · Building the messages for an LLM

A `ChatPromptTemplate` stores the roles and wording you write once. When you use it, LangChain fills the blanks with this request’s values. The result is the prompt the chat model will read.

**Interview recall: look at the input, then the requested output.**

| What do you see or need? | Method to recall |
|---|---|
| One template string: `"Classify {review}"` | `from_template(...)` |
| A list of roles: `[("system", ...), ("human", ...)]` | `from_messages(...)` |
| Filled-in text as one string | `format(...)` |
| Filled-in chat messages with their roles | `format_messages(...)` |

### 6. How do I build a template and fill it?

**Answer — `from_messages()` defines the template. `format_messages()` fills it.**

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer using only the supplied reviews."),
    ("human", "Reviews: {context}\nQuestion: {question}"),  # "Reviews:" starts here.
])

values = {
    "context": "The nurses were kind.",
    "question": "How were the nurses?",
}

messages = prompt.format_messages(**values)
print(messages[1].content)
```

**Printed output**

```text
Reviews: The nurses were kind.
Question: How were the nurses?
```

**Why does the output say `Reviews:`?** That word was already in `prompt`. The `**values` argument fills only `{context}` and `{question}`. If you change `Reviews:` to `Feedback:` in the template, the same dictionary gives you `Feedback: The nurses were kind.`

### 6a. Fill the blanks to get a SystemMessage followed by a HumanMessage.

**Correct choices, in order — `from_messages`, `"system"`, `format_messages`.**

```python
sentiment_template = ChatPromptTemplate.from_messages([
    ("system", "You're an expert in sentiment classification. {response_format}"),
    ("human", "Classify this review: {review}"),
])

messages = sentiment_template.format_messages(
    response_format="Answer with one word (negative or positive).",
    review="The nurses were friendly and attentive.",
)
```

**Why** — The opening `[` and the role labels tell you the input is a list of messages. The requested output is also messages, so use the two methods ending in `_messages`: `from_messages` to build, `format_messages` to fill. `ChatPromptTemplate.from_template("...")` takes one string and assumes the human role.

### 7. What does `prompt.format_messages(**values)` return?

**Answer — A list of two message objects in this example.** Each tuple becomes one message:

| Position | Type | Content |
|---|---|---|
| `messages[0]` | `SystemMessage` | The instruction from the `"system"` tuple. |
| `messages[1]` | `HumanMessage` | The review and question from the filled `"human"` tuple. |

### 8. What does `prompt.format(**values)` return?

**Answer — One string.** Printing it shows the whole prompt:

```text
System: Answer using only the supplied reviews.
Human: Reviews: The nurses were kind.
Question: How were the nurses?
```

`Human:` comes from the role. `Reviews:` comes from your wording.

### 8a. With a plain `PromptTemplate`, where are the placeholders recorded, what does `.format()` return, and how does a chat model receive it?

**Correct choices — `input_variables`, a plain string, and a single `HumanMessage`.**

```python
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template("Summarize this review: {review}")
print(prompt.input_variables)                  # ['review']
text = prompt.format(review="The nurses were kind.")
print(text)                                    # Summarize this review: The nurses were kind.
reply = chat_model.invoke(text)                # Sends the string as one HumanMessage.
```

**Why** — Creating the template records the name `review`. Formatting fills that blank and gives you text. Only when you pass that text to the chat model does LangChain treat it as a user message.

### 9. What does `prompt.invoke(values)` do? When does the LLM answer?

**Answer — Look at the object before `.invoke()` to see what runs.**

```python
ready_prompt = prompt.invoke(values)     # ChatPromptValue holding the filled messages
reply = chat_model.invoke(ready_prompt)  # AIMessage holding the model's answer
```

In `prompt | chat_model | StrOutputParser()`, each pipe passes the result to the next step. The parser extracts the answer text.

### 10. Where does the question enter the full review chain?

**Answer — `review_chain.invoke("How were the nurses?")`.** Both branches receive that string. Together they build the dictionary you filled by hand in question 6.

```python
{
    "context": reviews_retriever | format_reviews,
    "question": RunnablePassthrough(),
}
```

### 11. Where does `{context}` get its review text?

**Answer — `reviews_retriever` searches for reviews.** It’s defined earlier, for example with `reviews_retriever = vector_store.as_retriever()`. Then `format_reviews` prepares the matching documents as text.

### 12. What does `RunnablePassthrough()` put in `{question}`?

**Answer — `"How were the nurses?"`.** It returns the original input unchanged, so the model gets both the reviews and the question to answer.

```python
from langchain_core.runnables import RunnablePassthrough

passthrough = RunnablePassthrough()
question = passthrough.invoke("How were the nurses?")
print(question)  # How were the nurses?
```

In your review chain, the dictionary entry `"question": RunnablePassthrough()` stores that returned string under the key `"question"` for the prompt.

### 12a. How do I tell `RunnablePassthrough` and `RunnableSequence` apart?

**Interview answer — A passthrough returns the input it receives. A sequence runs steps in order, giving each step the previous step’s output.**

Suppose both branches receive `"How were the nurses?"`:

```python
{
    "question": RunnablePassthrough(),
    "context": reviews_retriever | format_reviews,
}
```

| Branch | What happens |
|---|---|
| `question` · passthrough | Receives the question string and returns exactly `"How were the nurses?"`. |
| `context` · sequence | The retriever receives the question and returns matching documents. Then `format_reviews` receives **those documents** and produces review text, e.g. `"The nurses were kind."`. |

**Write the sequence explicitly.** Assume `reviews_retriever` is already set up to search your review collection.

```python
from langchain_core.runnables import RunnableSequence

def format_reviews(docs):
    return "\n".join(doc.page_content for doc in docs)

context_chain = RunnableSequence(reviews_retriever, format_reviews)
context = context_chain.invoke("How were the nurses?")
print(context)  # Retrieved review text
```

The pipe shorthand is `context_chain = reviews_retriever | format_reviews`. In either form, the question goes to the retriever, and its list of documents goes to `format_reviews`.

**Recall cue:** When you see `A | B`, read it as “B receives whatever A returned.” When you see `RunnablePassthrough()`, ask “What went in?” That’s what comes out.

### 13. What do the four main LangChain message types carry?

| Message type | What it carries |
|---|---|
| `SystemMessage` | App instructions. |
| `HumanMessage` | User input. This template also includes the retrieved reviews here. |
| `AIMessage` | The model’s reply or its request to call a tool. |
| `ToolMessage` | The result from a tool the model called. |

### 14. Where does the `developer` role fit?

**Answer — OpenAI’s API accepts `developer` for app instructions.** This LangChain template uses `"system"` for its instruction. In tuple syntax, `"human"` and `"user"` are aliases, as are `"ai"` and `"assistant"`.

## LangChain · Structured output and debugging

### 15. What does `.with_structured_output(NoticeEmailExtract)` do with the Pydantic class?

**Correct choice — It converts the class into instructions that tell the model what to return.**

**Why** — “Instructions” means the schema: the field names and types defined in `NoticeEmailExtract`. The screenshot shows the class name and leaves its fields unspecified.

1. **Before the answer:** LangChain supplies the schema so the LLM knows which details to extract from the email.
2. **After the answer:** LangChain parses and validates what the LLM returned. On success, you get a `NoticeEmailExtract` instance.

**Why “filters the reply” is wrong** — A filter can keep or discard keys in an existing reply. If the reply is missing a required field, deleting other keys cannot supply it. The schema guides the LLM while it is writing the answer, and validation checks that the required field is present.

### 16. What function do you call to inspect the execution steps of a LangChain chain?

**Correct choice — `set_debug(True)`.**

**Why** — It turns on debug output. When you run the chain, the console shows intermediate steps so you can see where the data first goes wrong.

**How to debug your review chain**

1. Turn on debugging and run one question you know how to check:

   ```python
   from langchain_core.globals import set_debug

   set_debug(True)
   try:
       review_chain.invoke("How were the nurses?")
   finally:
       set_debug(False)
   ```

2. Read the console output in order. Did the retriever find a review about nurses? Did the prompt receive that review in `context` and the original question in `question`?
3. Find the first unexpected value or error. Fix that step and rerun the same question. The `finally` block turns debugging off even if the chain fails.
