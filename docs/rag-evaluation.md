# RAG (Retrieval-Augmented Generation) Evaluation

Retrieval-Augmented Generation (RAG) systems combine LLMs with semantic document retrievers. Ensuring your system cites the correct sources and doesn't hallucinate is a major challenge.

AgentAudit provides deterministic scoring specifically tailored for auditing RAG pipelines.

---

## RAG Assertions

### 1. expected_sources
Asserts that the list of documents returned by the chatbot contains the expected sources.

```yaml
cases:
  - id: check-refund-sources
    input: "How can I return an item?"
    expected_sources:
      - "refund_policy.md"
```

### 2. citation_required
If set to `true`, the test case will fail if the adapter returns an empty citation list (or `None`). This guarantees that your RAG pipeline is actually performing lookups instead of fabricating answers.

```yaml
cases:
  - id: check-citations
    input: "Explain shipping standard rates."
    citation_required: true
```

---

## Scoring Metrics

### Source Match Score
The `source_match_score` is a decimal value between `0.0` and `1.0` representing the percentage of expected source files that were successfully retrieved and cited:

$$\text{Source Match Score} = \frac{\text{Number of Matched Expected Sources}}{\text{Total Expected Sources}}$$

If `expected_sources` are defined, AgentAudit checks if the expected document paths or names exist as substrings in the returned citation tags list.

---

## Hallucination Risk Heuristics

AgentAudit evaluates whether an answer has a high **hallucination risk** using several heuristic layers. A test case is marked with `hallucination_risk = true` if:

1.  **Missing Citations**: `citation_required` is `true` but the returned sources list is empty.
2.  **Poor Source Quality**: The computed `source_match_score` is below `0.5` (meaning more than half of the expected sources are missing).
3.  **Fact Omissions**: The case defines `expected_contains` (required facts), but the response text fails to contain these substrings.

When marked, a distinct warning icon (🚨) is rendered next to the test case in terminal outputs, Markdown files, and the interactive HTML dashboard.
