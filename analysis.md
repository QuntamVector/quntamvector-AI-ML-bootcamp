# Kubernetes AI Bots — Technical Analysis

> **Analyst perspective:** Senior GenAI / Platform Engineer  
> **Date:** June 12, 2026

---

## Overview

Both projects live under the same umbrella of **AI-assisted Kubernetes management**, but they solve fundamentally different problems. One is a **reactive, user-facing conversational interface**; the other is a **proactive, autonomous background daemon**. They share a common GenAI framework (CrewAI), the same LLM provider (Google Gemini), and a shared `K8sMethodBuilderAgent` pattern — suggesting they evolved from a common codebase.

---

## Project 1 — `ins-ai-k8-chatbot`

### What It Is

A **real-time, multi-room WebSocket chatbot** that allows users to query a live Kubernetes cluster using plain English. It translates natural language into executable Kubernetes Python SDK method calls, runs them against the actual cluster, and returns formatted responses in a browser UI.

### Architecture Diagram

```
Browser (index.html)
    │
    ├─── HTTP :8080  ──────────────────> aiohttp static file server
    │
    └─── WebSocket :8765 ─────────────> ChatServer
                                             │
                                        RoomManager
                                        (multi-room, 50-msg history)
                                             │
                                        UserInputProcessor
                                             │
                                    ┌────────┴────────────┐
                                    │                     │
                              K8sMethodBuilder      KubernetesObjectParser
                              (CrewAI Crew)         (response beautifier)
                                    │
                            K8sMethodBuilderAgent
                            (gemini-3.1-flash-lite)
                                    │
                             K8sRulesTool (RAG-like rules lookup)
                                    │
                             eval(method_signature)
                                    │
                             kubernetes Python client
                                    │
                              Live K8s Cluster
```

### Component Breakdown

#### `server.py` — Entry Point
Launches two concurrent services: an `aiohttp` HTTP server at `:8080` to serve the static `index.html`, and a WebSocket server at `:8765` handled by `ChatServer`. Uses `asyncio` throughout.

#### `chat_server.py` — WebSocket Server
Manages the full connection lifecycle:
- Assigns each connecting user a UUID and auto-generated username (`User-XXXXX`)
- Supports message types: `join`, `chat`, `leave`, `set_name`
- On each `chat` message, broadcasts the user's text to all room members, then calls `UserInputProcessor.process()` asynchronously and broadcasts the bot's response back to the room
- Maintains a `RoomManager` to allow multiple isolated chat rooms

#### `room_manager.py` — Room State
- `ChatRoom`: holds members (dict), a message history (`deque(maxlen=50)`), and an `asyncio.Lock` for thread-safe member management
- `RoomManager`: creates rooms on demand, lists all active rooms on `welcome`

#### `models.py` — Data Models
Clean Pydantic-style `@dataclass` definitions for `User`, `Message`, and `MessageType` enum (`CHAT`, `JOIN`, `LEAVE`, `SYSTEM`, `ERROR`, `BOT`). Messages serialize to dicts with ISO timestamps.

#### `modules/user_input_processor.py` — The AI Execution Engine
This is the **core intelligence layer**. The flow is:

1. Takes raw user text as input
2. Hands it to `K8sMethodBuilder.kickoff()` (async CrewAI execution)
3. Extracts `method_signature` from the structured JSON output (e.g., `CoreV1Api().list_pod_for_all_namespaces()`)
4. **Calls `eval(signature, K8S_API_SCOPE)`** — executes the generated SDK call against a real cluster
5. Passes the raw K8s response object into `KubernetesObjectParser.parse()` → `beautifyJson()`
6. Returns HTML-formatted string to the chat UI

> **Critical Design Note:** The use of `eval()` with a scoped namespace (`K8S_API_SCOPE`) is intentional but a security consideration — the scope is locked to known K8s API classes only, which mitigates arbitrary code execution. In production, this would warrant a stricter allowlist or a sandboxed execution model.

#### `agents/k8s_method_builder_agent.py` — The LLM Agent
A CrewAI `Agent` configured as a **"K8s SDK Builder"**:
- **LLM:** `gemini/gemini-3.1-flash-lite` (temperature=0 — deterministic outputs)
- **Tool:** `K8sRulesTool` — a static knowledge base injected as a tool call, acting as a lightweight RAG substitute
- Backstory encodes the full API surface: which API class maps to which resource, method naming conventions (`list_namespaced_X`, `read_namespaced_X`, etc.), cluster-scoped vs namespaced rules

#### `tasks/k8s_method_builder_task.py` — Structured Output Task
The task enforces a Pydantic `MethodSignature` output model via `output_json=MethodSignature`. This forces the LLM to return `{"method_signature": "CoreV1Api().list_pod_for_all_namespaces()"}` — no free-form text, making downstream `eval()` reliable.

#### `tools/k8s_rules_tool.py` — Knowledge Base Tool
A static CrewAI `@tool` that returns a compact prompt-engineering ruleset encoding:
- API class → resource type mapping
- Method name normalization rules (e.g., `pvc` → `persistent_volume_claim`)
- Cluster-scoped vs namespaced resources
- Parameter ordering rules (`body` is positional, not a kwarg)

This is a clever pattern: instead of a vector DB, the domain rules are small enough to embed directly in a tool response.

#### `modules/k8s_object_parser.py` — Deep Response Parser
A 800-line hand-crafted parser with dedicated extractors for **17 resource types**: Pod, Deployment, StatefulSet, DaemonSet, ReplicaSet, Job, CronJob, Service, Ingress, ConfigMap, Secret, Node, PVC, PV, ResourceQuota, NetworkPolicy, Event. Each extractor flattens the verbose K8s Python client objects into clean, renderable summaries. The `beautifyJson()` method converts these to HTML `<br>`-delimited strings for the chat UI.

#### `static/index.html` — Chat UI
A single-file, no-dependency browser app:
- Left sidebar with room list (defaults: `#general`, `#random`, `#dev`) + "new room" creation
- Chat area with color-coded messages: blue (self), white (others), teal (bot), gray (system)
- Auto-reconnecting WebSocket with 3s retry
- Shift+Enter for newline, Enter to send
- Inline HTML rendering of bot responses (enables the `<br>`-formatted K8s data)

### Technology Stack

| Layer | Technology |
|---|---|
| WebSocket server | `websockets` (asyncio) |
| HTTP server | `aiohttp` |
| AI framework | CrewAI 1.14.6 |
| LLM | Gemini Flash Lite (`gemini/gemini-3.1-flash-lite`) |
| K8s client | `kubernetes` Python SDK v31 |
| Output validation | Pydantic v2 |
| UI | Vanilla HTML/CSS/JS |

### What Queries It Can Handle

```
"List all pods in the default namespace"
"Get the logs from pod nginx-abc123"
"Show me all deployments with less than 2 replicas"
"Describe the node worker-01"
"List all PVCs that are Pending"
"Get details of ingress my-ingress in namespace prod"
```

### Strengths
- Clean async architecture throughout — no blocking calls on the WebSocket event loop
- Structured output via Pydantic prevents hallucinated method signatures
- Comprehensive object parser supports virtually all standard K8s resource types
- Room-based isolation allows multiple concurrent users/sessions
- Zero external dependencies for the UI

### Weaknesses & Risks
- `eval()` on LLM-generated code is a security surface — injection via a crafted user prompt is a real risk
- `gemini-3.1-flash-lite` is a lightweight model — complex multi-step queries may fail
- No authentication on the WebSocket server — anyone with network access can query the cluster
- HTML is injected directly into `bubble.innerHTML` without sanitization — XSS risk
- Memory (ChromaDB is in `requirements.txt`) is unused — CrewAI's built-in memory is dormant

---

## Project 2 — `Insp-kube-pilot` (ins-ai-kube-pilot)

### What It Is

An **autonomous Kubernetes Issue Diagnosis Agent** — a headless background service designed to run **inside** a Kubernetes cluster. It continuously watches cluster resources, detects anomalies using a rules engine, deduplicates events via Redis, queues alerts, and dispatches them to a CrewAI agent that performs root cause analysis (RCA) and generates remediation steps. Alerts are then sent to Slack/Teams/webhooks.

### Architecture Diagram

```
K8s Cluster
    │
    ├── Pods / Nodes / PVCs / Deployments
    │         │  (Kubernetes Watch API — long-poll streaming)
    │         ▼
    │     K8sWatcher (4 daemon threads)
    │     [watch_resource loop per resource type]
    │         │
    │     WatcherRules (check_pod / check_node / check_pvc / check_deployment)
    │     [rule-based condition checks → Alert objects]
    │         │
    │         ▼
    │     QueueManager
    │     ├── In-memory Queue (maxsize=1000)
    │     └── Redis deduplication cache
    │         KEY = "alert:{resource}:{ns}:{name}:{reason}"
    │         TTL = 14400s (4 hours default)
    │         │
    │         ▼
    │     Consumer Thread (_consume_loop)
    │     [exponential backoff retry, 3 attempts]
    │         │
    │         ▼
    │     K8sConsumer → K8sPilotCrew (CrewAI)
    │         │
    │     K8sDiagnosisAgent
    │     (gemini-2.5-flash)
    │         │
    │     K8sDiagnosisTask
    │     [root_cause, remediation_steps, validation_method]
    │         │
    │         ▼
    │     Alert Dispatcher
    │     [Teams / Slack / Webhook]
    │
    └── Redis (separate K8s Deployment)
```

### Component Breakdown

#### `main.py` — Entry Point & Orchestrator
The main function wires everything together:
1. Loads K8s config (in-cluster via ServiceAccount token, or falls back to `~/.kube/config` for dev)
2. Runs the `K8sMethodBuilder` agent once at startup (smoke test — verifies the LLM is reachable)
3. Starts a Redis-backed `QueueManager` consumer thread
4. Spawns **4 daemon threads**, each running an independent `K8sWatcher` watch loop for: pods, nodes, PVCs, deployments

#### `modules/watcher.py` — K8sWatcher
The watcher runs an infinite `kubernetes.watch.Watch()` loop per resource type:
- Handles `ADDED` and `MODIFIED` events (skips `DELETED`)
- Calls the per-resource `check_fn` (rule checker) on each event object
- Handles `HTTP 410 ResourceVersion expired` by restarting the watch (standard K8s watch pattern)
- Routes generated `Alert` objects to `self.dispatch()` → logs + optionally sends to webhooks

#### `modules/rules.py` — WatcherRules (The Detection Engine)

**Pod Rules:**
| Condition | Severity | Trigger |
|---|---|---|
| `phase == "Pending"` | WARNING | PodPending / Unschedulable |
| `phase in ("Failed", "Unknown")` | CRITICAL | Phase{Failed/Unknown} |
| `waiting.reason == "CrashLoopBackOff"` | CRITICAL | Container CrashLoopBackOff |
| `waiting.reason == "OOMKilled"` | CRITICAL | Container OOMKilled |
| `waiting.reason in ("ImagePullBackOff", "ErrImagePull")` | WARNING | Image pull failure |
| `terminated.reason == "OOMKilled"` | CRITICAL | OOMKilled (post-mortem) |
| `terminated.exit_code != 0` | WARNING | NonZeroExit |
| `status.reason == "Evicted"` | WARNING | Pod eviction |

**Node Rules:**
| Condition | Severity |
|---|---|
| `Ready == "False"` | CRITICAL |
| `DiskPressure == "True"` | CRITICAL |
| `MemoryPressure == "True"` | CRITICAL |
| `PIDPressure == "True"` | WARNING |
| `NetworkUnavailable == "True"` | CRITICAL |
| `spec.unschedulable == True` | WARNING (cordoned) |

**Deployment Rules:** CRITICAL if `available_replicas == 0`, WARNING if `available_replicas < spec_replicas`.

**PVC Rules:** WARNING for `Pending` phase, CRITICAL for `Lost` phase.

**Event Rules:** Filters `type == "Warning"` events. CRITICAL for `CrashLoopBackOff`, `OOMKilling`, `FailedScheduling`, etc.

#### `modules/queue_manager.py` — Redis-Backed Queue
A two-layer deduplication system:

1. **In-memory queue** (`queue.Queue(maxsize=1000)`) — non-blocking `put_nowait()` drops events if full
2. **Redis NX (set-if-not-exists)** with TTL — key `alert:{resource}:{ns}:{name}:{reason}` is set atomically. Default TTL is 4 hours, preventing repeated LLM calls during a prolonged incident

The consumer loop uses **exponential backoff retry** (`base_delay * 2^attempt`) with 3 attempts before dropping the alert.

#### `modules/logger.py` — Alert Data Model
`@dataclass Alert` with `Severity` enum (`CRITICAL`, `WARNING`, `INFO`). Routes CRITICAL to `log.critical()` and WARNING to `log.warning()` — compatible with log-based alerting pipelines (CloudWatch, Datadog, etc.).

#### `agents/k8s_diagnosis_agent.py` — The Diagnosis LLM Agent
A CrewAI `Agent` configured as a **"Kubernetes Diagnostics Specialist"**:
- **LLM:** `gemini/gemini-2.5-flash` (temperature=0 — deterministic analysis)
- **No tools** — operates purely on the context provided in the task description
- `allow_delegation=False` — single-agent execution

> Uses `gemini-2.5-flash` (higher capability) vs the chatbot's `gemini-3.1-flash-lite`. This is correct — RCA requires deeper reasoning than method name generation.

#### `tasks/k8s_diagnosis_task.py` — The Diagnosis Task
Formats the serialized `Alert` dict into a structured prompt requesting:
1. **ROOT CAUSE:** Single primary cause in 1–2 sentences
2. **REMEDIATION:** Ordered steps (max 5)
3. **VALIDATION:** How to verify the fix

### Infrastructure Requirements

```yaml
# Required Kubernetes resources:
- ServiceAccount: k8s-watcher (in-cluster auth)
- ClusterRole: get/list/watch on pods, nodes, pvcs, events,
               deployments, statefulsets, daemonsets, jobs
- ClusterRoleBinding
- Deployment: ai-kube-pilot (1 replica)
  Resources: 250m CPU request / 500m limit, 64Mi–512Mi memory
- Deployment: redis:alpine (1 replica, port 6379)
- ConfigMap: REDIS_HOST, REDIS_PORT, REDIS_TTL
- Secret: GENAI_API_KEY
```

### Technology Stack

| Layer | Technology |
|---|---|
| Watch mechanism | `kubernetes.watch.Watch()` (streaming) |
| Thread model | Python `threading.Thread` (daemon) |
| Queue | Python `queue.Queue` + Redis NX dedup |
| AI framework | CrewAI 1.14.5 |
| LLM | Gemini 2.5 Flash (`gemini/gemini-2.5-flash`) |
| K8s client | `kubernetes` Python SDK v31 |
| Cache / dedup | Redis 7.4 + `redis-py` |
| Alert dispatch | Slack/Teams webhook (pluggable) |
| Deployment | Docker → Kubernetes Deployment |

### Strengths
- Production-ready event deduplication via Redis
- Resilient watch loops with `HTTP 410` handling (correct K8s watch pattern)
- Exponential backoff retry on the consumer side
- Clear separation of concerns: Watch → Rules → Queue → Consumer → Agent
- RBAC principle of least privilege — only `get/list/watch`, no write permissions
- Thread-per-resource model allows independent failure isolation
- Pluggable alert dispatch (webhook URL via env var)

### Weaknesses & Risks
- `K8sConsumer.event_handler()` calls `crew.run()` **synchronously** — slow LLM calls back up the queue
- No structured output on the diagnosis task — response parsing is implicit
- `main.py` crashes at boot if the LLM smoke test returns unexpected format
- Single consumer thread is a bottleneck under high alert volume
- Redis connection initialized at module import — hard crashes if Redis is unreachable at startup

---

## Side-by-Side Comparison

| Dimension | `ins-ai-k8-chatbot` | `Insp-kube-pilot` |
|---|---|---|
| **Trigger model** | Reactive (user-driven) | Proactive (event-driven) |
| **User interaction** | Real-time browser UI | Headless background daemon |
| **Primary use case** | Query / inspect cluster state | Detect failures, generate RCA |
| **AI task** | NL → K8s SDK method generation | Root cause analysis + remediation |
| **LLM model** | `gemini-3.1-flash-lite` (lightweight) | `gemini-2.5-flash` (capable) |
| **Output format** | HTML-formatted K8s resource data | Free-form RCA text → webhook |
| **Structured output** | Yes (Pydantic `MethodSignature`) | No (free-form task) |
| **State management** | In-memory rooms + message history | Redis dedup cache + in-memory queue |
| **Transport** | WebSocket + HTTP | Threading + Redis queue |
| **K8s auth** | `kubeconfig` (dev) / in-cluster | In-cluster ServiceAccount (prod-grade) |
| **Multi-tenant** | Yes (multi-room) | No (single cluster watcher) |
| **Alert dispatch** | N/A | Slack / Teams webhook |
| **CrewAI pattern** | Async kickoff | Sync kickoff |
| **Deployment** | Local / Docker | Kubernetes Deployment |
| **RBAC** | Not specified | `ClusterRole` (read-only) |
| **Deduplication** | None | Redis NX + TTL |
| **Retry logic** | None | Exponential backoff (3 attempts) |

---

## Shared Components & Code Reuse

Both projects share the same `K8sMethodBuilderAgent` + `K8sDiagnosisTask` (method builder variant) + `K8sRulesTool` pattern:

```
agents/k8s_method_builder_agent.py   ← identical structure, different LLM model
tasks/k8s_method_builder_task.py     ← slight variation in expected_output format
tools/k8s_rules_tool.py              ← identical
crews/k8s_method_builder.py          ← identical
```

The chatbot came first as the NL-to-K8s translation proof of concept, and kube-pilot evolved from it adding the autonomous watcher, Redis, and RCA layer on top.

---

## Key Design Patterns Used

### 1. Intent-to-SDK Translation (Chatbot)
```
User: "show me crashlooping pods"
  → LLM generates: CoreV1Api().list_pod_for_all_namespaces(field_selector="status.phase=Failed")
  → eval() executes it → parser formats response → UI renders
```

### 2. Event-Driven RCA Pipeline (Kube Pilot)
```
K8s event → Rule check → Alert → Redis dedup → Queue → CrewAI → Remediation text → Webhook
```
Rule-based fast filtering → LLM-based deep analysis is the right separation of concerns.

### 3. Tool-as-Knowledge-Base Pattern
Both agents use `K8sRulesTool` — a static CrewAI `@tool` that returns prompt-engineering rules as a string. A pragmatic substitute for a vector DB when the knowledge domain is small and stable.

---

## Production Readiness Assessment

| Concern | Chatbot | Kube Pilot |
|---|---|---|
| Security (eval/XSS) | ⚠️ Needs hardening | ✅ Read-only RBAC |
| Observability | ⚠️ Print statements only | ✅ Structured logging |
| Scalability | ⚠️ Single process | ⚠️ Single consumer thread |
| Fault tolerance | ⚠️ No retry on LLM calls | ✅ Exponential backoff |
| Auth / AuthZ | ❌ No WebSocket auth | ✅ ServiceAccount RBAC |
| Deduplication | ❌ None | ✅ Redis NX + TTL |
| Structured output | ✅ Pydantic output_json | ⚠️ Free-form text |
| Config management | ⚠️ `.env` only | ✅ ConfigMap + Secrets |
| Containerization | ✅ Dockerfile present | ✅ Dockerfile + K8s manifests |

---

## Recommendations

### For `ins-ai-k8-chatbot`
1. **Replace `eval()` with a whitelist executor** — validate API class and method name against a hardcoded allowlist before executing
2. **Add `html.escape()` before setting `bubble.innerHTML`** — prevent XSS from K8s object names
3. **Add WebSocket authentication** — even a simple token check on the `welcome` handshake
4. **Add streaming support** — stream the LLM response token by token for better UX
5. **Upgrade LLM** — promote `gemini-3.1-flash-lite` → `gemini-2.5-flash` for better accuracy

### For `Insp-kube-pilot`
1. **Add `output_json` structured output to `K8sDiagnosisTask`** — define a `RCAReport` Pydantic model for reliable webhook formatting
2. **Move `K8sConsumer.event_handler()` to async** or use a thread pool to parallelize concurrent LLM calls
3. **Add Redis connection health check at startup** with retry backoff
4. **Enable the Teams/Slack alert dispatch** — `_send_webhook()` exists but `dispatch()` never calls it (commented out in `watcher.py`)
5. **Implement the `WATCH_RESOURCES` env-var parser** — documented in README but resources are hardcoded in `main.py`
