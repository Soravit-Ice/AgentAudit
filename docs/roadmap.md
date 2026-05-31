# AgentAudit Roadmap

This document outlines the milestones and features planned for the development of AgentAudit.

---

## Phase 1: MVP Launch (v0.1.0) - *Current*

*   [x] Core Pydantic Models for Test suites, cases, assertions, and reporting aggregates.
*   [x] Pluggable target adapters (Mock, HTTP, Command).
*   [x] Deterministic scoring assertions (contains, exact, regex, max latency, expected policy refusals).
*   [x] Local Thai and English refusal check heuristics.
*   [x] Basic RAG evaluations (source lists containing, citations checks, matching score, and hallucination warnings).
*   [x] Defensive safety test packs.
*   [x] Multi-format reporting (Rich Terminal, JSON, Markdown, beautiful Glassmorphism HTML dashboards).
*   [x] CLI execution tools.
*   [x] GitHub Actions CI pipelines integration.

---

## Phase 2: Orchestration integrations & LLM Judges (v0.2.0)

*   **Semantic similarity judges**: Add optional LLM-as-a-Judge capability using OpenAI, Anthropic, or local Ollama endpoints to evaluate answers without strict substring rules.
*   **Built-in SDK adapters**: Ship pre-configured adapters for popular AI libraries:
    *   LangChain / LangGraph
    *   LlamaIndex
    *   AutoGen
*   **DuckDB Local storage**: Log execution metrics locally to track regression graphs and accuracy trends over time.

---

## Phase 3: Developer Dashboard & Visual UI (v0.3.0)

*   **Interactive Web UI**: Run a local webserver (`agentaudit dashboard`) to view historical results, build test suites, execute evals visually, and inspect RAG citation details.
*   **Safety playground**: An interactive prompt injection sandbox to try jailbreak ideas and save them immediately as test cases.
