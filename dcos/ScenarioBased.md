# Scenario-Based AI System Design

Interview scenarios from video #2, with the reviewed design improvements.

## Scenario #1 — RAG Over 10 Million Documents

**Question:** Design a RAG system over **10 million documents**, with **citations** and **latency under 2 seconds**.

First clarify whether the latency target means **time to first token** or **time to complete the answer**. Agree on the percentile, peak query rate, and concurrency—for example, **p95 under 2 seconds at the agreed peak load**.

Split the architecture into **ingestion** and **query serving**.

### 1. Ingestion — Prepare and Index Documents

| Step | Design |
|---|---|
| **Parse** | Extract text and document structure from incoming PDFs, documents, and web pages. |
| **Deduplicate** | Remove identical content so it does not waste storage or pollute retrieval. |
| **Chunk** | Start with semantic or document-structure-based chunking. Evaluate whether chunks preserve the information needed to answer questions. |
| **Attach metadata** | Record tenant IDs, access permissions, document versions, timestamps, and source URLs. Preserve the identifiers and offsets needed for citations. |
| **Estimate capacity** | Estimate the number of chunks and vectors, embedding dimensions, and index overhead. **Illustrative assumption:** ten chunks per document turns ten million documents into **100 million vectors**. |
| **Embed and index** | Generate embeddings in batches and store them in an ANN index. Choose partitioning and capacity using the estimated index size and query workload. |
| **Handle changes** | Incrementally process updated documents and remove deleted content. Refresh affected embeddings, metadata, and cached results. |

### 2. Query Serving — Retrieve, Rerank, and Generate

| Step | Design |
|---|---|
| **Authenticate and authorize** | Derive tenant identity and document permissions from the authenticated user. Apply that scope to both keyword and vector retrieval. |
| **Check the cache** | Reuse a cached result only when its authorization scope and underlying content remain valid. |
| **Hybrid retrieval** | Run **BM25 keyword search** and **dense vector search** in parallel. Both must respect the same access restrictions. |
| **Merge results** | Use a defined fusion method, such as **Reciprocal Rank Fusion (RRF)**, to combine the ranked lists. Remove duplicate chunks. |
| **Rerank and select context** | Rerank a bounded candidate set, then select relevant chunks within a context-token budget. |
| **Generate the answer** | Supply the selected evidence to the model and request an answer with source references. If the evidence is insufficient, return that limitation instead of producing an unsupported answer. |

### 3. Citations — Connect Claims to Evidence

Each chunk should retain:

- A **stable document ID and version**.
- A **chunk ID**.
- **Exact character offsets** in the indexed text.
- A **source URL**.

| Check | Approach |
|---|---|
| **Reference validity** | Validate that returned citation IDs belong to the retrieved, authorized evidence. Build citation links from stored metadata. |
| **Version accuracy** | Resolve citations to the document version used to generate the answer. |
| **Evidence support** | Evaluate whether the cited passage actually supports the associated claim. A valid citation ID alone does not establish this. |

### 4. Keep Latency Under 2 Seconds

| Control | Approach |
|---|---|
| **Define the measurement** | Specify first-token versus complete-answer latency, the target percentile, and the traffic level. |
| **Budget the request path** | Account for query embedding, retrieval, fusion, reranking, context preparation, and model generation. |
| **Parallelize retrieval** | Execute independent keyword and vector searches concurrently. |
| **Bound expensive stages** | Limit reranking candidates and context size. If the target covers the complete answer, also control output length. |
| **Cache carefully** | Cache repeated queries and frequently used embeddings while respecting permissions and content freshness. |
| **Benchmark filtering** | Enforce authorization during retrieval, and measure filtering performance. Highly selective filters can increase ANN traversal time. |

### 5. Evaluate the Design

| Area | What to measure |
|---|---|
| **Retrieval** | Whether the required evidence appears in the retrieved results—for example, **Recall@k**. |
| **Answer quality** | Whether the answer addresses the question and remains grounded in the retrieved evidence. |
| **Citations** | Whether references resolve correctly and support the associated claims. |
| **Performance** | First-token and complete-answer latency, including p95, under realistic concurrent load and cache-hit/cache-miss conditions. |
| **Access and freshness** | Whether unauthorized, deleted, outdated, or newly restricted content can appear in retrieval or cached responses. |

### Trade-off

**Higher recall improves evidence coverage, but can increase retrieval latency and introduce noisy context.** Tune retrieval breadth, reranking, and context selection together, using measured answer quality and latency.


## Scenario #2 — Fluent but Wrong RAG Answers

**Question:** Your RAG chatbot produces fluent but incorrect answers. How would you debug it?

Start by identifying **where the evidence is missing or being misused**. The transcript separates retrieval from generation; I’d also explicitly inspect the context actually delivered to the model.

### 1. Locate the Failing Stage

| Check | What it indicates |
|---|---|
| **Is the correct passage present in the top-K retrieved results?** | If absent, investigate the retrieval path. |
| **Was that passage included in the actual model input?** | If retrieved but omitted, investigate reranking, context selection, or truncation. |
| **Is the passage present in the model input, but the answer still wrong?** | Investigate grounding instructions, context ordering, distracting information, and evidence sufficiency. |

### 2. Debug Retrieval

| Area | What to inspect |
|---|---|
| **Source availability** | Confirm that the required document and current version were successfully indexed. |
| **Query rewriting** | Check whether rewriting changed the user’s intended meaning or removed important terms. |
| **Chunking** | Check whether the answer was split across chunks or separated from necessary context. |
| **Embedding quality** | Check whether relevant passages are being ranked poorly for the question. |
| **Metadata filters** | Check whether incorrect filters excluded relevant, authorized documents. |
| **Hybrid search** | Inspect keyword and vector results separately, then examine their combined ranking. |

### 3. Debug Generation

| Area | What to inspect |
|---|---|
| **Prompt grounding** | Check whether instructions clearly require answers to follow the supplied evidence. |
| **Context ordering** | Check whether important evidence is buried or displaced by less relevant material. |
| **Distracting chunks** | Check whether unnecessary or irrelevant passages are confusing the answer. |
| **Insufficient evidence** | Check whether the model answers confidently despite lacking the information needed. |

### 4. Evaluate Fixes Systematically

| Evaluation | Approach |
|---|---|
| **Retrieval quality** | Use real user questions with known relevant passages. Measure whether those passages appear in the retrieved results. |
| **Answer quality** | Check whether answers address the question and are supported by the supplied evidence. |
| **Regression coverage** | Preserve failed production questions as test cases and rerun them after changes. |

### Additional Diagnostic — Supply the Correct Context

Give the model the known correct passage while keeping the model and instructions fixed.

- If the answer improves, investigate retrieval and context selection further.
- If it remains wrong, investigate generation and grounding further.

This narrows the investigation; it does not prove a single cause, because changing the context also changes its ordering and distractions.

## Scenario #3 — Agent Keeps Calling the Wrong Tool

**Question:** Your agent repeatedly selects the wrong tool. How would you fix it?

Start by inspecting the **full agent trajectory** to understand where the decision went wrong.

### 1. Trace the Failed Execution

| Stage | What to inspect |
|---|---|
| **User input** | What was the user asking the agent to accomplish? |
| **Planning/routing** | What task was the agent attempting to perform? |
| **Tool selection** | Which tool did it select? Was that tool appropriate for the task? |
| **Arguments** | What arguments did it generate? |
| **Tool response** | What did the tool return? |
| **Final answer** | How did the agent use the tool’s response? |

### 2. Improve Tool Definitions

| Common problem | Improvement |
|---|---|
| **Vague descriptions** | Clearly describe what the tool does and when it should be used. |
| **Overlapping responsibilities** | Give each tool a specific responsibility and make the boundaries clear. |
| **Weak parameter schemas** | Specify required arguments, use enums for constrained choices, and validate inputs before execution. |
| **Continued confusion between tools** | Add a few short examples demonstrating correct tool-selection patterns. |

### 3. Protect High-Risk Tool Calls

| Control | Purpose |
|---|---|
| **Confirmation steps** | Require confirmation before executing a high-risk action. |
| **Policy validation** | Check whether the requested action is permitted before calling the tool. |

### 4. Evaluate the Fix — Suggested Addition

| Evaluation | What it checks |
|---|---|
| **Tool-selection accuracy** | Does the agent choose the expected tool for representative user requests? |
| **Argument accuracy** | Does it supply the correct, valid arguments? |
| **Execution outcome** | Does the selected tool successfully perform the intended action? |

Include requests that previously caused confusion when comparing the original and revised tool definitions.

### Trade-off

**Stronger constraints improve reliability**, but can increase **latency, token usage, cost, and engineering complexity**.


## Scenario #4 — Parallel Training vs. Sequential Generation

**Question:** Why can LLM training run in parallel while inference generates an answer one token at a time?

The key difference is **whether the correct preceding tokens are already available**.

### 1. Training vs. Inference

| Aspect | Training | Standard autoregressive inference |
|---|---|---|
| **Available information** | The complete correct training sequence is already known. | The prompt is known; the answer must be generated. |
| **Previous tokens** | Uses the correct preceding tokens from the training example. | Uses the tokens generated so far. |
| **Parallelism** | Next-token predictions at many positions can be computed simultaneously. | Each generation step depends on the preceding generated tokens. |

### 2. Example — Generating “New Delhi”

Using words to illustrate the steps:

| Step | Available context | Next output |
|---|---|---|
| **1** | “The capital of India is” | “New” |
| **2** | “The capital of India is New” | “Delhi” |

During inference, the second step uses the result of the first.

During training, both correct prefixes already exist in the example, so their next-token predictions can be computed in parallel.

### 3. Additional Technical Clarifications

| Point | Explanation |
|---|---|
| **Parallel training does not allow looking ahead** | A **causal attention mask** prevents each prediction from accessing future tokens, even though the complete training sequence is available. |
| **Inference still uses parallel computation** | Servers can process multiple requests concurrently and batch work. Prompt processing (**prefill**) and answer generation (**decode**) are distinct phases. The sequential dependency concerns successive tokens within one standard autoregressive answer. |


## Scenario #5 — Standardize LLM Access Across Teams

**Question:** Multiple teams in your company use LLMs. How would you standardize their access?

Introduce a **centralized LLM gateway** as the common entry point. Teams integrate with one stable API; the platform team manages providers, model upgrades, and routing centrally.

### 1. Gateway Responsibilities

| Responsibility | What the gateway handles |
|---|---|
| **Authentication** | Identify the calling team or application. |
| **Quotas and rate limits** | Control usage by team and throttle requests when limits are exceeded. |
| **Model routing** | Route requests to the appropriate model or provider. |
| **Prompt-template management** | Centrally manage reusable prompt templates. |
| **Policy checks** | Block requests that violate policy before they reach the model. |
| **Logging and cost attribution** | Record usage and attribute costs to the responsible team. |
| **Retries and fallbacks** | Handle temporary failures and switch to another model when necessary. |

### 2. Expected Operational Behavior

| Situation | Gateway behavior |
|---|---|
| **A provider becomes unavailable** | Fail over to another model or provider. |
| **A team exceeds its quota** | Throttle that team’s requests. |
| **A request violates policy** | Block it before calling the model. |
| **The platform changes providers or upgrades models** | Handle the change behind the stable API used by teams. |

### 3. What to Monitor

| Metric | What it helps reveal |
|---|---|
| **Latency** | Whether requests are becoming slower. |
| **Error rate** | Whether failures are increasing. |
| **Cost by team** | Which teams are consuming the budget. |
| **Model usage patterns** | Which models teams use and how frequently. |
| **Safety violations** | Which requests violate policy. |
| **Fallback success rate** | Whether fallback paths successfully recover requests. |

### 4. Suggested Production Additions

| Addition | Purpose |
|---|---|
| **Multiple gateway instances** | Avoid making one gateway instance a single point of failure. |
| **Bounded retries and request deadlines** | Prevent recovery attempts from extending requests indefinitely. |
| **Compatible fallback models** | Verify that fallbacks support required capabilities, such as tool calling or structured output, and preserve policy requirements. |
| **Sensitive-data redaction** | Prevent logs from unnecessarily exposing prompts, credentials, or sensitive content. |

### Trade-off

A centralized gateway adds **platform complexity**, while providing **centralized governance, cost control, and simpler management of model integrations**.

## Scenario #6 — High Evaluation Scores, but Unhappy Users

**Question:** Your AI system scores well on evaluations, but users keep complaining. What might be wrong?

**Core idea:** Your evaluations may not reflect real production usage. Correct answers alone do not guarantee that users can complete their tasks.

### 1. Identify the Mismatch

| Dimension | What the evaluation might test | What users actually experience |
|---|---|---|
| **Question quality** | Clean, straightforward questions. | Vague, messy, ambiguous requests. |
| **Correctness** | Whether an answer is technically correct. | Whether it is clear and useful. |
| **Speed** | Answer quality without considering response time. | Frustration with slow responses. |
| **Task completion** | Success on an individual question. | Whether the system helps finish the overall task. |

### 2. Diagnose and Improve

| Step | What you do | Why it matters |
|---|---|---|
| **Inspect failed sessions** | Review actual production conversations where users struggled. | Reveals failures your evaluation set missed. |
| **Group the complaints** | Look for slow responses, repeated misunderstandings, rephrased questions, and users abandoning tasks. | Identifies recurring failure patterns. |
| **Update the evaluation set** | Add representative examples of those production failures. | Makes future evaluations reflect real usage. |
| **Track product outcomes** | Measure whether users accomplish their goals alongside model quality. | Connects technical performance to user success. |

### 3. What to Measure

| Metric | What it tells you |
|---|---|
| **Task completion rate** | Are users successfully finishing their tasks? |
| **Escalation rate** | How often does the interaction require additional help? |
| **User correction rate** | How often must users correct the system? |
| **Repeat-question rate** | How often do users ask again or rephrase because the first response did not help? |

## Scenario #7 — Scaling RAG from 10,000 to 100 Million Documents

**Question:** Your RAG system works for 10,000 documents but fails at 100 million. What changes?

**Core idea from video #2:** At this scale, RAG becomes a **distributed systems problem**.

| Area | What changes | Why it matters |
|---|---|---|
| **Sharding and distributed retrieval** | Distribute the index across machines; queries may search multiple shards. | A single index on one machine is no longer practical at this scale. |
| **Merge and rerank globally** | Collect results from different shards, combine them, and rerank the combined candidates. | Adds coordination overhead and **tail latency**. |
| **Early metadata filtering** | Apply tenant and permission constraints early in retrieval. | Reduces the search space and avoids retrieving content that must later be discarded. |
| **Incremental indexing** | Update the affected content instead of rebuilding the entire index. | Full reindexing becomes impractical. |
| **Versioning and freshness** | Track document versions and keep indexed content current. | Updates must remain manageable as the collection grows. |
| **Caching** | Cache frequently requested queries and repeated retrieval results. | Avoids repeating the same retrieval work. |

**Trade-off highlighted in the video:** Better recall at this scale comes with higher **latency, infrastructure cost, and system complexity**.

## Scenario #8 — Prompt Injection Through Retrieved Documents

**Question:** Your agent retrieves a document containing malicious instructions. How do you prevent those instructions from controlling the agent?

**Core idea from video #2:** Treat retrieved documents as **untrusted data**. Security must be enforced outside the prompt.

| Control | What the design should do |
|---|---|
| **Separate instructions from content** | Clearly distinguish the agent’s instructions from retrieved document text. Prompt separation alone is insufficient protection. |
| **Prevent documents from authorizing actions** | Retrieved content must not directly trigger tool execution. |
| **Validate tool calls server-side** | Check proposed tool calls before executing them. |
| **Apply least privilege** | Give the agent only the permissions it needs. |
| **Require approval for sensitive actions** | Use explicit approval or human review for actions such as payments, deletions, and sensitive external API calls. |
| **Use injection detection as an additional layer** | Detection can help, but it can be bypassed and should not be the primary defense. |

**Key takeaway:** A malicious document should not gain the authority to execute actions merely because the agent retrieved it.

## Scenario #9 — Tenant Isolation in a Shared AI Application

**Question:** Multiple customers use the same AI application. How do you prevent one customer’s data or actions from affecting another?

**Core idea from video #2:** Isolation must cover **data, compute, caches, and tools**.

| Area | What the design must isolate |
|---|---|
| **Data** | Keep each tenant’s documents, embeddings, chat history, and memory isolated. Authenticate tenant identity and enforce access on the server. |
| **Compute** | Apply tenant-specific quotas and rate limits so one tenant cannot monopolize shared resources. |
| **Caches** | Prevent cached information or responses from being reused across unauthorized tenant boundaries. |
| **Tools and actions** | Ensure API calls, file access, and other actions operate within the correct tenant’s scope. |

**Key takeaway:** Tenant isolation extends beyond document retrieval to every part of the application that handles customer information or executes actions.

**Trade-off:** Stronger isolation improves **security and reliability**, but increases **cost, implementation complexity, and operational overhead**.

## Scenario #10 — Retrieved Documents Give Conflicting Answers

**Question:** Your RAG system retrieves two documents that disagree. How should it answer?

**Core idea from video #2:** Use document metadata to resolve the conflict, and make unresolved disagreements explicit.

| Check | What the system should do |
|---|---|
| **Version and timestamp** | Check whether one document is newer or supersedes the other. |
| **Source authority** | Determine which source is authoritative for the information requested. |
| **Resolve the conflict** | Prioritize the current, authoritative source when the metadata establishes which applies. |
| **Conflict remains unresolved** | Explain that the sources disagree instead of guessing or presenting one answer as certain. |

**Design requirement:** Preserve **versions, timestamps, and source information** during ingestion.

**Trade-off:** Reliable conflict handling requires good **metadata and document governance**.

## Scenario #11 — AI Traffic Grows 100×: How Do You Scale Inference?

**Core idea from video #2:** Combine **caching, batching, replicas, and queuing**, based on where the system is constrained.

### 1. Identify the Bottleneck First

The video starts by asking whether the constraint is the **model, GPUs, request rate, or latency requirements**. That determines which scaling techniques will help.

### 2. Apply the Four Techniques

| Technique | How it works | What it improves |
|---|---|---|
| **Caching** | Reuse repeated query results, retrieval results, or prompt prefixes where possible. | Reduces repeated work. |
| **Batching** | Group requests arriving around the same time and process them together instead of handling every request separately. | Improves **GPU utilization and throughput**. |
| **Replicas + load balancing** | Run multiple model instances behind a load balancer so they can serve requests in parallel. | Increases serving capacity. |
| **Queuing** | When incoming traffic exceeds available capacity, hold requests and process them as capacity becomes available. | Handles traffic spikes without immediately dropping requests. |

### 3. Balance the Trade-offs

The video emphasizes that these techniques affect one another.

| Change | Benefit | Trade-off |
|---|---|---|
| **Larger batches** | More requests processed together; higher throughput. | Can increase response latency. |
| **More replicas** | More requests served in parallel. | Higher infrastructure cost. |
| **Queue excess requests** | Protects the system when capacity is exceeded. | Adds waiting time for users. |

For example, increasing batch size may help the system process more requests overall, but users can wait longer. Adding replicas increases capacity, but costs more. Queuing absorbs excess demand while making the wait visible to users.

**Interview takeaway from the video:** Scaling inference requires a combination of these techniques, with explicit trade-offs between **throughput, latency, and cost**.

## Scenario #12 — Agent Memory Becomes Stale or Incorrect

**Question:** How do you prevent agent memory from becoming stale or incorrect?

**Core idea from video #2:** Memory provides **context**, not unquestioned truth or permanent knowledge. Stored information can stop being correct.

### 1. Why Memory Becomes Stale

| Change | What it means for stored memory |
|---|---|
| **User preferences change** | A previously stored preference may no longer apply. |
| **A task becomes irrelevant** | Context retained for that task may no longer be useful. |
| **Facts become outdated** | A stored fact may no longer be correct. |

### 2. Keep Memory Reliable

| Approach | What the system should do | Why it matters |
|---|---|---|
| **Attach metadata and check freshness** | Record the **last-updated time, source, and confidence** for memories. | Helps assess whether the information is still current. |
| **Validate important memories** | Check that important stored information is still correct before using it. | Prevents blindly trusting a previous memory. |
| **Support forgetting** | **Expire, archive, or remove** memories that are old, unused, low-confidence, or contradictory. | Prevents memory quality from degrading over time. |

**Key takeaway:** Memory needs **validation, freshness checks, and forgetting** to remain useful and reliable.

## Additional Interview Q&A — Spoken Answers

Implementation answers for interview practice; these extend the video-based scenario notes.

### 1. How do you prevent unauthorized tool calls and enforce human approval?

> The model proposes a tool call; application code authorizes it. Before execution, I validate the tool, arguments, customer ownership, and business policy. For sensitive actions, I pause with a LangGraph interrupt and checkpoint the proposed action. An authorized reviewer approves the exact action and arguments through an authenticated endpoint. On resume, I recheck permissions and approval. Rejection, expiry, or changed arguments prevents execution. Writes use backend-enforced idempotency keys to prevent duplicates.

### 2. How do you enforce customer scope?

> I derive customer identity and permissions from the authenticated session on the server. The model can suggest an order ID, but it cannot override the customer scope. Retrieval applies access filters, database queries enforce ownership, and every tool endpoint checks that the requested resource belongs to that customer. I also scope conversation memory, checkpoint access, and cached responses. If an order belongs to another customer, the backend denies access before returning its information.

### 3. What happens when evidence is insufficient?

> I identify which required facts are missing. If the request needs clarification, I ask the customer. If retrieval missed evidence, I allow a bounded number of additional searches or tool calls within the same authorized scope and time budget. If the gap remains, I return the supported facts, explain what is unresolved, and abstain or escalate. Any action whose prerequisites are unverified stays blocked. Model confidence alone does not establish that the evidence is sufficient.

### 4. How do you measure task success, unsafe actions, latency, and cost?

> I define success as a verified outcome—for example, a ticket created for the correct customer or a supported answer that resolves the request. I track completion rate and human handoffs separately. For safety, I distinguish blocked unauthorized attempts from unsafe actions actually executed, including missing approvals or customer-scope violations. For latency, I measure end-to-end and per-stage percentiles, separating human approval time. For cost, I include model, retrieval, tools, and infrastructure, including retries and failed attempts, and report cost per verified resolution.
