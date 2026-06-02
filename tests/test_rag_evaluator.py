from agentaudit.models import TestCase
from agentaudit.rag.evaluator import evaluate_rag


def test_citation_required_assertion() -> None:
    case = TestCase(id="rag-1", input="Explain", citation_required=True)

    # Success: has citations
    assertions, score, risk = evaluate_rag(case, "Output text", ["doc_a.md"])
    assert len(assertions) == 1
    assert assertions[0].success is True
    assert risk is False

    # Fail: empty citations
    assertions_fail, score_fail, risk_fail = evaluate_rag(case, "Output text", [])
    assert len(assertions_fail) == 1
    assert assertions_fail[0].success is False
    assert risk_fail is True


def test_expected_sources_assertion() -> None:
    case = TestCase(
        id="rag-2",
        input="Explain",
        expected_sources=["refund_policy.md", "shipping_policy.md"],
    )

    # Success: both documents retrieved
    assertions, score, risk = evaluate_rag(case, "Output", ["refund_policy.md", "shipping_policy.md", "extra.md"])
    assert len(assertions) == 1
    assert assertions[0].success is True
    assert score == 1.0
    assert risk is False

    # Partial success: only one source matched
    assertions_partial, score_partial, risk_partial = evaluate_rag(case, "Output", ["refund_policy.md"])
    assert len(assertions_partial) == 1
    assert assertions_partial[0].success is False
    assert score_partial == 0.5
    # score < 0.5, or fact omitting rules: here score = 0.5. Let's see if risk is marked
    # If partial, the RAG matcher checks if score < 0.5. Here score == 0.5, so risk is False unless facts failed.
    assert risk_partial is False

    # Poor retrieval: zero matched
    assertions_poor, score_poor, risk_poor = evaluate_rag(case, "Output", ["unrelated.md"])
    assert score_poor == 0.0
    assert risk_poor is True


def test_hallucination_risk_fact_checks() -> None:
    case = TestCase(
        id="rag-3",
        input="Query",
        expected_contains=["7 days"],
    )

    # Correct response
    _, _, risk = evaluate_rag(case, "Items are returnable in 7 days.", [])
    assert risk is False

    # Hallucinating response (lacks expected contains fact)
    _, _, risk_hallucination = evaluate_rag(case, "Items are not returnable.", [])
    assert risk_hallucination is True
