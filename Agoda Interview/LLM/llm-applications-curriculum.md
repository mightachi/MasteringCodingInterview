# Production-Grade LLM Applications: Multi-Agent Systems, Document Intelligence & Scale

**A 7-Month Engineering Curriculum for Building Real LLM Products**

---

## A Note Before You Start

The previous curriculum I wrote for you was about *training* LLMs — research and infrastructure work. This one is different. This is about *building products on top of LLMs*, which is a fundamentally different discipline. You'll write more application code, more glue code, more infrastructure code, and far fewer matrix multiplications.

Three honest things up front:

1. **This is not "prompt engineering."** The skill set you need spans distributed systems, software architecture, evaluation methodology, and operational discipline. Anyone can paste a prompt into ChatGPT. The market pays seniors $300K+ to build systems that ingest 50K documents/day, hit p95 latency under 800ms, cost under $0.01 per request, and don't hallucinate when the lawyers are watching.

2. **Most LLM tutorials are toys.** They show you LangChain in 100 lines and call it done. Production looks nothing like this. You will be writing your own orchestration code, your own evaluation harnesses, your own observability layers, your own fallback chains. Frameworks help — they don't replace the work.

3. **You will need to spend money.** Plan ~$300–$600 across the seven months on API calls (OpenAI, Anthropic, Cohere), managed services (a vector DB tier, an observability tool), and deployment (Modal or Fly.io credits). The capstone projects each spend $50–$150 in API costs by themselves.

The course has eleven phases. The two big resume projects sit in Phases 10A and 10B. Everything before exists to make them possible.

---

## Curriculum Overview

| Phase | Title | Duration | Outcome |
|------:|-------|---------:|---------|
| 0 | Prerequisites | 1 week | Python async, FastAPI, Docker, basic SQL |
| 1 | LLM API Mastery & Prompt Engineering | 3 weeks | Production prompting; model selection; tokens & cost |
| 2 | Structured Outputs & Function Calling | 2 weeks | Reliable schema-conformant outputs at scale |
| 3 | Embeddings, Vector Search & RAG Foundations | 3 weeks | Working naive RAG system |
| 4 | Advanced RAG | 3 weeks | Hybrid search, reranking, query rewriting, eval |
| 5 | Single-Agent Architectures | 3 weeks | ReAct, Plan-and-Execute, Reflection agents |
| 6 | Multi-Agent Systems | 3 weeks | Orchestrator patterns, LangGraph, state machines |
| 7 | Document Intelligence: Unstructured → Structured | 3 weeks | PDF/image extraction pipelines |
| 8 | Model Context Protocol (MCP) | 2 weeks | Build & deploy MCP servers exposing tools and resources |
| 9 | Production: Observability, Evaluation, Guardrails | 3 weeks | Telemetry, online + offline eval, safety layers |
| 10 | Scale, Latency & Cost Optimization | 3 weeks | Caching, batching, routing, async architectures |
| 11A | **Capstone 1: Document Intelligence + MCP** | 3 weeks | Production-grade extraction platform |
| 11B | **Capstone 2: OTA Conversational Agent** | 4 weeks | Multi-agent travel assistant at scale |
| 12 | Interview Preparation | 2 weeks | System design, project storytelling |

**Total: ~30 weeks (~7 months) at 15–20 hours/week.**

---

## Phase 0 — Prerequisites (1 week)

If you've shipped production Python services, skim and move on. If not, fix the gaps.

**Required skills going in:**
- **Async Python.** `asyncio`, `aiohttp`, `httpx`. You'll write a lot of concurrent I/O code.
- **FastAPI or equivalent.** REST APIs, dependency injection, Pydantic models, background tasks, streaming responses (SSE).
- **Docker.** Multi-stage builds, compose files, basic networking.
- **A SQL database** — Postgres preferred. CTEs, indexes, JSON columns.
- **Redis** — caching, pub/sub, basic data structures.
- **Git workflow** — branching, PR discipline. Goes without saying.

**Resources**
- FastAPI's official tutorial (work through it cover to cover)
- *Async IO in Python* by Real Python (their async series)
- The `httpx` documentation (you'll use this more than `requests`)

**Exit criteria:** You can scaffold a containerized FastAPI service with async endpoints, Postgres, and Redis in under 90 minutes from a blank directory.

---

## Phase 1 — LLM API Mastery & Prompt Engineering (3 weeks)

### Goals

Move past "I called the OpenAI API once." Master the surface area of modern LLM APIs, understand the cost/latency/quality tradeoffs of every major model, and learn the prompting patterns that actually hold up in production.

### Topics

**Week 1 — The API Landscape**
The major providers — OpenAI, Anthropic, Google (Gemini), Mistral, Cohere — and what each is genuinely good at. Open-source via Together, Fireworks, Groq, Cerebras. Model families: frontier (Claude Opus/Sonnet 4.x, GPT-5, Gemini 2.5), mid-tier (Haiku, Mini), small/fast (3B–8B class). Tokenization differences. The economics: input vs. output token costs, prompt caching pricing, batch API discounts.

**Week 2 — Production Prompting Patterns**
System prompts as software contracts. Few-shot prompting — when it helps, when it hurts. Chain-of-thought, step-back prompting, self-consistency. XML structuring for Claude, JSON-mode coercion for GPT. Role separation. Instruction layering. Negative examples. Anti-patterns: kitchen-sink prompts, vibes-based iteration, untested edits.

**Week 3 — Model Selection & Cost Engineering**
Building intuition for which model to use when. The classic ladder: route easy queries to a small model, hard ones to a frontier model, with the small model judging when to escalate. Token accounting — how to estimate per-request cost before you ship. Prompt caching (Anthropic style, OpenAI style, Gemini style) and how to architect for it. Why your "GPT-4 wrapper" needs to be a "model-agnostic wrapper."

### Resources
- Anthropic's prompt engineering documentation — read all of it.
- OpenAI's "Prompt engineering" guide.
- The DSPy paper and library (Stanford) — "programming, not prompting." Conceptually important even if you don't adopt the framework.
- Eugene Yan's blog posts on LLM patterns.
- Hamel Husain's writing on LLM evaluation.

### Exercises
1. Build a tiny CLI tool that calls 4 different model providers behind one interface (`generate(prompt, model="claude-haiku-4-5") → text`). Add streaming.
2. Take one task — say, "summarize a news article in three bullets" — and benchmark 6 models on it: cost per call, p50/p95 latency, qualitative output quality across 50 articles. Build a spreadsheet.
3. Implement prompt caching for a long-document Q&A workflow. Measure the cost reduction.

### Exit criteria
Given a new use case, you can pick the right model within 2 minutes and justify it on cost/latency/quality grounds.

---

## Phase 2 — Structured Outputs & Function Calling (2 weeks)

### Goals

Free-form text is for chatbots. Real applications need structured data — JSON, validated against schemas, that downstream code can consume safely. This is where the majority of "LLM doesn't work in production" complaints originate, and where the fix is mostly engineering.

### Topics

**Week 1 — Structured Outputs**
Native JSON mode (OpenAI, Anthropic). Tool/function calling as a structured-output mechanism. Grammar-constrained decoding (Outlines, llama.cpp grammars). Pydantic as the source of truth. The Instructor library pattern. Self-healing on validation failure: re-ask with the error message in context. Why "give me JSON" prompts fail at scale and how to bulletproof them.

**Week 2 — Function/Tool Calling Deep Dive**
The tool-calling protocols across providers (they are *not* the same). Parallel tool calls. Forced tool choice vs. auto. Multi-turn tool conversations. Designing tool schemas — the descriptions are the prompt; treat them as such. Pitfalls: too many tools, overlapping tools, tools with side effects, retry semantics.

### Resources
- The Pydantic documentation (V2). Master `Field`, validators, discriminated unions.
- Jason Liu's Instructor library — read the source, not just the README.
- Anthropic's "Tool use" documentation.
- OpenAI's "Function calling" documentation.
- The Outlines library for constrained generation.

### Exercises
1. Build an extractor for structured contact info from messy text. 100 test cases. Measure field-level accuracy and JSON validity rate.
2. Build a multi-tool agent (5 tools — weather, calculator, web search, file read, calendar). Stress test with 50 ambiguous queries. Where does it pick the wrong tool? Why?
3. Implement a self-correcting JSON pipeline: if Pydantic validation fails, feed the error back to the model with a retry. Measure success rate before and after.

### Exit criteria
You produce schema-conformant JSON with >99.5% reliability on your test suite, and you know exactly what to do when it fails the other 0.5% of the time.

---

## Phase 3 — Embeddings, Vector Search & RAG Foundations (3 weeks)

### Goals

Most real LLM applications need to ground responses in private data. RAG (Retrieval-Augmented Generation) is the dominant pattern. You'll build a working naive RAG system, then in the next phase, learn why naive RAG falls over in production and how to fix it.

### Topics

**Week 1 — Embeddings**
What embeddings are (vector representations of meaning). The current best embedding models: OpenAI `text-embedding-3-large`, Cohere Embed v3+, Voyage AI, BGE, Nomic. Dimensionality, similarity metrics (cosine vs. dot product vs. Euclidean — and when each applies). Matryoshka embeddings. Domain adaptation.

**Week 2 — Vector Stores & Search**
The vector database landscape — Pinecone, Weaviate, Qdrant, Milvus, Postgres with `pgvector`, ChromaDB. When you need a vector DB vs. when `pgvector` is enough. HNSW vs. IVF indexes — what you actually need to know. Filtering by metadata. Hybrid stores.

**Week 3 — Naive RAG: End-to-End**
The pipeline: ingest → chunk → embed → store → retrieve → augment → generate. Chunking strategies (fixed-size, recursive, semantic, document-structure-aware). The prompt template for stuffing context. Why naive RAG fails: bad retrieval, context dilution, hallucination from irrelevant context.

### Resources
- Pinecone's "Learn" docs — best free RAG curriculum on the internet.
- LlamaIndex documentation (even if you don't use the framework, the concepts are well-explained).
- The original RAG paper (Lewis et al., 2020).
- The MTEB leaderboard on Hugging Face — know it cold.

### Exercises
1. Build a RAG system over your own personal knowledge base (notes, bookmarks, whatever). Aim for ~10K documents.
2. Benchmark 3 embedding models on retrieval quality. Use a hand-labeled query/relevant-doc set of 50 examples. Compute recall@5, recall@10, MRR.
3. Try 4 chunking strategies on the same corpus. Measure how each affects retrieval quality.

### Exit criteria
You can build a naive RAG system end-to-end in a weekend, and you can articulate exactly why naive RAG is insufficient for production.

---

## Phase 4 — Advanced RAG (3 weeks)

### Goals

Production RAG looks nothing like naive RAG. This phase turns you into someone who can debug a RAG system that's returning the wrong answer 30% of the time and bring it down to 5%.

### Topics

**Week 1 — Retrieval Quality**
Hybrid search (dense + sparse via BM25). Why BM25 still beats embeddings on exact-match queries. Reranking with cross-encoders (Cohere Rerank, BGE Reranker, Voyage Rerank). Query expansion and rewriting. HyDE (Hypothetical Document Embeddings). Multi-query retrieval. Parent-document and small-to-big patterns.

**Week 2 — Advanced Retrieval Strategies**
Query routing — different queries need different indexes or different retrieval methods. Multi-hop retrieval for queries requiring chained reasoning. Graph RAG (Microsoft GraphRAG, Neo4j-based patterns) — when knowledge graphs actually pay off vs. when they're complexity for its own sake. Contextual retrieval (Anthropic's pattern). Late chunking.

**Week 3 — RAG Evaluation**
The metric hierarchy: retrieval quality (recall, precision, MRR) → answer quality (faithfulness, relevance, completeness) → user-facing metrics (CSAT, task completion). Building a golden eval set — how to assemble 100–500 query/answer pairs that actually measure what matters. Ragas, TruLens, DeepEval frameworks. LLM-as-judge for faithfulness scoring with known biases.

### Resources
- Anthropic's "Contextual Retrieval" blog post (this is the current state of the art for many workloads).
- Microsoft's GraphRAG paper and repository.
- Ragas documentation and the supporting paper.
- Jerry Liu's (LlamaIndex) talks on production RAG.
- *Towards LLM Observability* by Hamel Husain — the section on RAG evaluation.

### Exercises
1. Add hybrid search + reranking to your Phase 3 RAG system. Measure improvement on your hand-labeled eval set.
2. Build a query router that classifies queries into 4 types and routes each to a different retrieval pipeline.
3. Implement Anthropic's contextual retrieval pattern from scratch. Measure cost and quality vs. baseline.
4. Build a Ragas-based eval pipeline that runs nightly against your RAG system and flags regressions.

### Exit criteria
Given a failing RAG system, you can diagnose where in the pipeline it's failing (retrieval vs. ranking vs. generation) and prescribe a fix grounded in measurement.

---

## Phase 5 — Single-Agent Architectures (3 weeks)

### Goals

Understand the core agent patterns before stacking them into multi-agent systems. Most "multi-agent" problems are actually single-agent problems solved badly.

### Topics

**Week 1 — The Core Loop**
Agents are LLMs in a loop with tool access. The ReAct pattern (Reason + Act). Planning vs. reacting. Tool selection. Stopping conditions. Error handling and retry. Why agents fail: tool hallucination, infinite loops, context overflow, lost-in-the-middle problems.

**Week 2 — Agent Patterns**
ReAct, Plan-and-Execute, ReWOO, Reflexion, Tree-of-Thoughts. Reflection patterns (self-critique, self-correction). Memory: short-term (conversation context), long-term (vector store of past interactions), episodic, semantic. The "agent loop budget" — bounding cost and time per turn.

**Week 3 — State Management**
Conversation state, agent state, tool state. Checkpointing for resumability. Human-in-the-loop interrupts (approval flows, clarification requests). The durable-execution problem — what happens when your process dies mid-loop. Temporal, Inngest, restate.dev for durable agent workflows.

### Resources
- The original ReAct paper (Yao et al., 2022).
- The Reflexion paper (Shinn et al., 2023).
- LangGraph documentation — read the conceptual guides even if you choose not to use LangGraph.
- Anthropic's "Building effective agents" guide — required reading.
- Simon Willison's blog on LLM tool use patterns.

### Exercises
1. Build a ReAct agent from scratch — no framework — in under 200 lines. Tools: web search, calculator, file read.
2. Add a reflection layer: after each tool call, the agent critiques whether it made progress.
3. Implement a stop-condition that bounds the agent to N tool calls or M dollars of spend, whichever comes first.
4. Use Temporal (or Inngest) to make your agent durable: kill the process mid-execution, restart it, verify it resumes correctly.

### Exit criteria
You can build a goal-directed agent from scratch and explain every design choice. You know when *not* to use an agent (often).

---

## Phase 6 — Multi-Agent Systems (3 weeks)

### Goals

Move from one agent doing one thing to many agents collaborating. This is where the real architectural decisions live.

### Topics

**Week 1 — Multi-Agent Patterns**
The orchestrator pattern (one router, many specialists). Hierarchical agents. Peer-to-peer agent networks. The "supervisor" pattern. Message-passing vs. shared-state architectures. Why most multi-agent systems should be a state machine with LLM-powered transitions, not "agents talking to each other."

**Week 2 — Frameworks: LangGraph, AutoGen, CrewAI, custom**
LangGraph (Anthropic/LangChain's graph-based orchestrator) — strengths and limitations. AutoGen (Microsoft) — conversation-driven. CrewAI — role-based. When to use a framework, when to roll your own. Honest tradeoffs: frameworks save weeks at first but cost months when you need to do anything unusual.

**Week 3 — Multi-Agent Challenges**
Failure modes: agents that disagree forever, agents that defer to each other, agents that hallucinate other agents' capabilities. Coordination cost — every additional agent multiplies tokens. Observability: tracing a single user request through 7 agents is hard. Determinism: making multi-agent systems testable.

### Resources
- The AutoGen paper (Wu et al., 2023).
- LangGraph documentation and the multi-agent examples.
- Anthropic's "How we built our multi-agent research system" blog post.
- "The Hidden Cost of Agentic Systems" — various recent analyses on token economics.

### Exercises
1. Build a 3-agent system using a state-machine pattern (no framework): a planner, an executor, a reviewer. Use it to solve a research-and-summarize task.
2. Implement the same system in LangGraph. Compare clarity, line count, and traceability.
3. Add full distributed tracing: every LLM call, tool call, and inter-agent message logged with trace IDs. Use LangFuse or Phoenix.

### Exit criteria
You can design a multi-agent system on a whiteboard, justify why it isn't a single agent with more tools, and predict the failure modes.

---

## Phase 7 — Document Intelligence: Unstructured → Structured (3 weeks)

### Goals

Real businesses run on PDFs, scans, emails, and spreadsheets. Turning these into structured data is one of the most valuable LLM use cases — and one of the trickiest. This phase covers the full pipeline.

### Topics

**Week 1 — PDF Parsing & OCR**
The PDF landscape: born-digital vs. scanned vs. hybrid. Text extraction libraries: `pypdf`, `pdfplumber`, `PyMuPDF`. OCR: Tesseract, PaddleOCR. Layout-aware parsers: Unstructured.io, LlamaParse, Marker, Docling, Surya. Managed services: Azure Document Intelligence, AWS Textract, Google Document AI, Reducto. The build-vs-buy tradeoff per document type.

**Week 2 — Multimodal Extraction**
Why vision-language models (Claude Sonnet 4.x, GPT-5 with vision, Gemini 2.5) are changing PDF extraction. Page-as-image extraction for tables and complex layouts. Two-pass extraction: cheap OCR pass + selective VLM pass for hard sections. Tables, forms, handwriting, multi-column layouts, footnotes, sidebars.

**Week 3 — Schema-First Extraction Pipelines**
Defining the target schema before writing any code. Pydantic models as contracts. Multi-pass extraction: extract → validate → re-extract on failure. Confidence scoring. Cross-field validation (totals match line items, dates are consistent). Human-in-the-loop fallback for low-confidence extractions. Batching for cost.

### Resources
- The Unstructured.io documentation and source code.
- Reducto's blog on production document parsing.
- Anthropic's PDF/vision API documentation.
- The Surya OCR project (open source, increasingly good).
- Eugene Yan's "Patterns for Building LLM-based Systems & Products" — the document extraction section.

### Exercises
1. Build a structured extractor for invoices (vendor, date, line items, totals, tax). Test set: 100 real invoices. Target: >95% field-level accuracy.
2. Compare 4 PDF parsing approaches on the same corpus (e.g., research papers): pypdf, Unstructured.io, LlamaParse, Claude vision. Measure quality and cost per page.
3. Implement multi-pass refinement with confidence scoring. Flag the bottom 5% confidence for human review.

### Exit criteria
You can design a production extraction pipeline for any document type, including budget and accuracy estimates.

---

## Phase 8 — Model Context Protocol (MCP) (2 weeks)

### Goals

MCP is Anthropic's open standard for exposing tools, data sources, and prompts to LLM applications in a uniform way. It's becoming the standard plug-and-play interface between agents and the rest of the world's software. Building MCP servers is a high-leverage skill right now.

### Topics

**Week 1 — MCP Fundamentals**
The protocol: clients, servers, transports (stdio, HTTP/SSE, streamable HTTP). The three primitives — tools, resources, prompts. The lifecycle: initialization, capability negotiation, request/response. Authentication patterns. Why MCP exists and what problems it actually solves vs. plain function calling.

**Week 2 — Building Production MCP Servers**
The Python and TypeScript SDKs. Designing tool surfaces — naming, descriptions, parameter schemas. Resources for read-only data exposure. Prompts as reusable templates. Versioning. Rate limiting, auth, and observability. Deploying an MCP server (containerized, behind a load balancer, with secrets management).

### Resources
- The official MCP specification at modelcontextprotocol.io.
- The MCP Python SDK and TypeScript SDK documentation and examples.
- Anthropic's MCP announcement and follow-up blog posts.
- The growing list of public MCP servers in the official registry — read source for a half-dozen of them.

### Exercises
1. Build a minimal MCP server that exposes one tool (e.g., a calculator) and run it locally with Claude Desktop or your own MCP client.
2. Build an MCP server that wraps a Postgres database, exposing schema as resources and parameterized queries as tools.
3. Deploy an MCP server behind HTTPS with proper authentication. Document the operational concerns: logging, rate limits, error handling.

### Exit criteria
You can build, deploy, and operate an MCP server end-to-end and explain the protocol semantics to a teammate.

---

## Phase 9 — Production: Observability, Evaluation, Guardrails (3 weeks)

### Goals

The difference between a demo and a product is operational maturity. This phase covers the three pillars: knowing what your system is doing, knowing whether it's any good, and keeping it from doing harm.

### Topics

**Week 1 — Observability**
Tracing across LLM calls, tool calls, and agent steps. LangFuse, Arize Phoenix, LangSmith, Helicone, Logfire — pick one and learn it deeply. What to log: full prompts, completions, latencies, token counts, errors, retries, user feedback. Cost attribution per request, per user, per feature. PII scrubbing in logs.

**Week 2 — Evaluation Systems**
The three loops: offline eval (against golden set), online eval (production samples), human eval (qualitative review). Building a golden set: 100–1000 carefully constructed examples. LLM-as-judge for scaled evaluation, with rubrics. Regression detection — your eval suite runs on every deploy. The "vibe check" problem and how to discipline it.

**Week 3 — Guardrails & Safety**
Input validation: jailbreak detection, prompt injection defenses, PII detection. Output validation: hallucination detection, policy compliance, toxicity. Tools: Guardrails AI, NeMo Guardrails, LlamaGuard, Lakera. Designing for failure: what does your system do when the LLM returns garbage? Refusal handling. The "human in the loop" tier for high-stakes decisions.

### Resources
- *Building LLM-Powered Applications* — Hamel Husain's writing on eval is the practical canon here.
- LangFuse and Arize Phoenix documentation.
- The Guardrails AI documentation.
- Simon Willison's blog posts on prompt injection (canonical references).

### Exercises
1. Add full tracing to your Phase 6 multi-agent system. View one user request as a flame graph showing every LLM call.
2. Build a golden eval set of 100 examples for your Phase 7 document extractor. Wire it into CI: every PR must run eval, regressions block the merge.
3. Add a prompt-injection defense layer to your agent. Test with a published prompt-injection benchmark.

### Exit criteria
You can stand up complete observability, eval, and guardrails for a new LLM system in under a week.

---

## Phase 10 — Scale, Latency & Cost Optimization (3 weeks)

### Goals

This is what the user explicitly asked about and it's the most under-taught area in the LLM application space. Master these techniques and you become disproportionately valuable.

### Topics

**Week 1 — Latency Optimization**
Where latency lives: network, queueing, prefill (first token), decode (subsequent tokens), tool calls. Streaming everything (SSE, WebSockets). Speculative decoding. Optimistic UI patterns. Parallelizing independent tool calls. Model selection by speed (Groq, Cerebras, Together for low-latency inference). Distillation: train a small model to mimic your prompt-engineered big model's outputs. P50 vs. p95 vs. p99 — and why p99 is what users remember.

**Week 2 — Cost Optimization**
Prompt caching across providers — restructure prompts to maximize cache hits. Model routing: cascade from cheap to expensive only when needed (use a classifier or the cheap model's confidence). Semantic caching with vector similarity (carefully — exact match is safer than you think). Batch APIs for non-realtime workloads (50% discount, hours of latency). Output token control — the cheapest token is one you don't generate. Stop sequences, max_tokens discipline, structured output to avoid verbose explanations.

**Week 3 — Scaling Architectures**
Async everything. Queue-based architectures (SQS, Redis streams, RabbitMQ) for non-realtime work. Horizontal scaling of inference fronts. Provider fallback chains for reliability (OpenAI down? Route to Anthropic). Rate limit management — token-bucket per provider, per key, with backpressure. Multi-region considerations. Auto-scaling agent workers.

### Resources
- Anthropic's documentation on prompt caching.
- OpenAI's "Optimizing latency" guide.
- Helicone and Portkey's blogs on cost optimization.
- The vLLM and TGI documentation (for self-hosted scaling).
- Eugene Yan's "Patterns" essay — the relevant sections.

### Exercises
1. Take your most expensive prompt and refactor it for prompt caching. Measure cost reduction over 1000 requests.
2. Build a 3-tier model router: classify query, route to small/medium/large model based on complexity. Measure cost and quality.
3. Convert a synchronous LLM workload to queue-based async. Measure how many concurrent requests your system handles before and after.
4. Implement a semantic cache with cosine-similarity matching. Set the threshold conservatively and measure hit rate + accuracy impact.

### Exit criteria
Given any LLM application, you can identify the top 3 optimizations and project their cost/latency impact within 25%.

---

## Phase 11A — Capstone 1: Document Intelligence Platform + MCP (3 weeks)

### Project Title

**"DocStream: A Production-Grade Document Extraction Platform with MCP Exposure"**

### What You're Building

A platform that ingests PDFs (and images), classifies them, extracts structured data using a multi-agent pipeline, validates the output, and exposes everything as an MCP server. Other LLM applications and AI assistants can connect to it as a tool source.

### Architecture

```
Upload → Classifier → Router → [Invoice / Contract / Form / Research Paper / ...]
                              ↓
                         Specialist Extractor Agent (per type)
                              ↓
                         Validator Agent (schema + cross-field)
                              ↓
                         Low Confidence? → Human Review Queue
                              ↓
                         Postgres (structured records)
                              ↓
                         MCP Server (exposes records as resources + extraction as a tool)
```

### Required Components

1. **Ingest API** — FastAPI endpoint accepting PDFs/images. Async background processing via a queue (Redis Streams or Celery).
2. **Classifier Agent** — identifies document type using a fast small model + few-shot prompts.
3. **Specialist Extractors** — one per document type, each with a Pydantic schema. Use Claude Sonnet 4.x or GPT-5 with vision for hard pages, cheaper model for easy ones.
4. **Validator Agent** — verifies extractions against schema + cross-field rules.
5. **Confidence Scoring** — every extracted field has a confidence score. Below threshold → human review.
6. **Storage** — Postgres with `pgvector` for both structured records and embedded chunks of source documents.
7. **MCP Server** — exposes:
   - `extract_document(file_uri)` as a tool
   - `query_records(filters)` as a tool
   - Individual extracted records as resources (so an LLM client can browse them)
8. **Observability** — every request traced (LangFuse or Phoenix), cost-per-document logged.
9. **Evaluation** — golden set of 100+ documents per type with hand-labeled ground truth, run nightly in CI.

### Production Targets

- **Throughput:** 100 documents/minute on commodity hardware (assuming external LLM API calls).
- **Accuracy:** >95% field-level on the eval set for invoice/form types.
- **Cost:** <$0.05 per document on average across types (this is achievable with model routing).
- **p95 latency:** <30 seconds per document end-to-end.

### Deliverables

1. **GitHub repo** — clean, with one-command Docker Compose setup.
2. **Architecture document** (5–10 pages) — your design decisions, alternatives considered, tradeoffs.
3. **Eval report** — accuracy per document type, cost analysis, failure modes catalog.
4. **Deployed MCP server** (Modal, Fly.io, or Railway) — publicly accessible, with auth.
5. **Demo video** (3–5 minutes) — walk through ingestion → extraction → MCP query from an LLM client.

### Resume Lines

- "Architected and shipped a production document intelligence platform processing 100+ documents/minute, achieving 96% field-level extraction accuracy at $0.04/document via tiered model routing."
- "Designed a multi-agent extraction pipeline (classifier → router → specialist extractor → validator) with confidence scoring and human-in-the-loop fallback for low-confidence outputs."
- "Built and operated a production MCP server exposing extracted records and extraction-as-a-tool to downstream LLM applications, including auth, rate limiting, and observability."

---

## Phase 11B — Capstone 2: OTA Conversational Agent (4 weeks)

### Project Title

**"TripMate: A Production Multi-Agent Travel Assistant"**

### What You're Building

A conversational agent for an online travel agency that handles search, booking, modifications, recommendations, and customer support across flights, hotels, and packages. The system is multi-agent, low-latency, cost-optimized, and built to scale to thousands of concurrent conversations.

### Architecture

```
User Message → Streaming Frontend
            ↓
         Orchestrator (state machine)
        ↙   ↓   ↘   ↘   ↘
   Search  Book Modify Recmd Support
   Agent   Agent Agent  Agent Agent
        ↘  ↓   ↙
         Tools Layer (mocked travel APIs + real APIs where free)
        ↓
   Memory Layer (user prefs, conversation, booking history)
        ↓
   Postgres + Redis + Vector Store
```

### Required Components

1. **Orchestrator** — a state machine (LangGraph or hand-rolled) that routes user messages to the right specialist agent and manages conversation state.
2. **Specialist Agents:**
   - **Search Agent** — flight/hotel search via mocked APIs (build realistic mocks; use Amadeus or Skyscanner test APIs if accessible).
   - **Booking Agent** — quote → confirm → reserve → pay (all mocked but with realistic state machines).
   - **Modification Agent** — change/cancel existing bookings.
   - **Recommendation Agent** — RAG-powered, grounded in a curated destinations/hotels knowledge base.
   - **Support Agent** — answers policy questions from a RAG layer over T&Cs.
3. **Memory Layer:**
   - Short-term: current conversation (Redis).
   - Long-term: user preferences and past bookings (Postgres).
   - Semantic: vector store of past resolved support conversations.
4. **Tools Layer** — clean MCP-compatible tool definitions; some tools call mocked services, some call real APIs.
5. **Streaming** — every agent response streamed token-by-token to the frontend (SSE).
6. **Guardrails** — PII handling for payment details, jailbreak filtering, hallucination checks on prices/availability.
7. **Observability & Eval** — full tracing; nightly eval on a 200-conversation golden set covering all 5 task types.

### Production Targets

- **Latency:**
  - First token within 1 second on 95% of turns.
  - Full response within 3 seconds for simple turns, streaming throughout for longer turns.
- **Cost:** <$0.05 per conversation on average (5–10 turns).
- **Scale:** 500 concurrent conversations on a single application server (async architecture).
- **Quality:** Task completion >85% on the eval set (across all 5 task types).

### Optimization Techniques You Must Apply

(These are the things you should highlight on your resume — *with the metrics*.)

- **Prompt caching** for system prompts and tool definitions (most providers support this; restructure to maximize hit rate).
- **Model routing:** Haiku-class for intent classification and routing; Sonnet/GPT-5-mini-class for response generation; frontier model only for complex multi-step reasoning.
- **Semantic caching** for common questions ("what's your cancellation policy?").
- **Parallel tool calls** when the agent needs flights AND hotels simultaneously.
- **Speculative streaming** — start streaming an "I'm looking up flights for you to Paris..." message while the actual tool call runs.
- **Distillation** for the intent classifier — fine-tune a small model to mimic your prompted classifier.

### Deliverables

1. **GitHub repo** — production-shaped, with Docker Compose for local dev.
2. **Deployed application** — Modal, Fly.io, or AWS, with a real URL you can point an interviewer at.
3. **Architecture document** — agent topology, state machine diagram, data flow, optimization decisions.
4. **Performance & cost report** — load test results, latency histograms (p50/p95/p99), cost-per-conversation breakdown, before/after for each optimization.
5. **Eval report** — task completion rates by category, common failure modes, hallucination audit.
6. **Demo video** (5–7 minutes) — walk through search → booking → modification → support.

### Resume Lines

- "Designed and built a production multi-agent conversational assistant for online travel, with 5 specialist agents (search, booking, modification, recommendation, support) orchestrated via a state-machine pattern."
- "Achieved p95 first-token latency under 1 second and average conversation cost of $0.04 across 5–10 turn sessions, through prompt caching, tiered model routing, semantic caching, and parallel tool execution."
- "Scaled to 500 concurrent conversations on a single application server via async architecture, with full distributed tracing, golden-set evaluation in CI, and PII/jailbreak guardrails."
- "Built memory layer combining Redis (conversation state), Postgres (user history), and vector store (past resolved cases) for personalized, grounded responses."

---

## Phase 12 — Interview Preparation (2 weeks)

### What you'll be asked

**System Design**
- "Design a customer-support chatbot for a SaaS company with 10K daily active users."
- "Design a RAG system over 10TB of internal documents with sub-second latency."
- "Design a multi-agent system that books travel."
- "How would you reduce LLM costs by 80% in an existing application?"

**Project Deep-Dives**
- "Walk me through the architecture of your document extraction platform."
- "Why did you choose a multi-agent design instead of one bigger agent?"
- "What was your hardest debugging session?"
- "What's the worst failure mode of your travel agent and how did you mitigate it?"

**Technical Depth**
- "How does prompt caching work? What needs to be true for a cache hit?"
- "When would you choose hybrid search over pure vector search?"
- "Walk me through how MCP works at the protocol level."
- "What's the difference between offline eval and online eval and when do you need both?"

### Practice

- Record yourself answering these out loud. Watch the playback. You'll cringe; that's the point.
- Find one peer working on similar things. Trade mock interviews weekly.
- Read system-design write-ups for production LLM systems (Notion AI, Linear AI, GitHub Copilot, Cursor).

### Exit criteria

You can talk for 60 minutes about your two capstone projects with no notes, drawing diagrams as you go.

---

## Tools You Will Have Used By the End

A non-exhaustive list, useful for your skills section:

- **Models:** Claude (Opus 4.7, Sonnet 4.6, Haiku 4.5), GPT-5 family, Gemini 2.5, Mistral, open-source via Together/Fireworks/Groq.
- **Frameworks:** LangGraph, LlamaIndex, DSPy, Instructor.
- **Vector stores:** Pinecone, Qdrant, pgvector.
- **Document parsing:** Unstructured.io, LlamaParse, Marker, Docling.
- **Observability:** LangFuse, Arize Phoenix, LangSmith.
- **Guardrails:** Guardrails AI, NeMo Guardrails.
- **Routing/Gateway:** Portkey, OpenRouter, Helicone.
- **Infra:** FastAPI, Postgres, Redis, Docker, Modal/Fly.io.
- **Durable workflows:** Temporal or Inngest.
- **MCP:** Anthropic's Python and TypeScript SDKs.

---

## Final Words

A few things worth saying directly:

**The market is wildly underpaying for application engineers who can actually ship production LLM systems.** It's overpaying for "prompt engineers" who can't. The first group quietly carries the second. Be in the first group.

**Build systems people can use, not demos.** A deployed application at a real URL, that an interviewer can click on and use, beats a thousand-star GitHub repo. The cost of keeping a small Modal/Fly.io deployment running for six months is $30. Pay it.

**Costs and latency are not afterthoughts.** Most LLM applications you'll see in interviews are over-engineered on the model side and under-engineered on operations. Make yours the opposite. The story of "I reduced costs by 60% via caching, routing, and structured outputs" is the most hireable story in this market right now.

**MCP is a leading indicator.** Right now, in 2026, MCP server-building skills are scarce and increasingly demanded. This won't last — six months from now everyone will have done it. Build yours now, write about it, publish the server, post about it on LinkedIn. The window is open.

Start with Phase 0 next Monday. Don't perfect the curriculum — execute it.

---

*End of curriculum. Total commitment: ~30 weeks at 15–20 hours/week. Two flagship projects on your resume. A complete skill stack for senior LLM application engineering roles.*
