from agentaudit.models import AssertionResult, TestCase


def evaluate_rag(case: TestCase, output: str, sources: list[str] | None) -> tuple[list[AssertionResult], float, bool]:
    """Evaluates RAG-specific criteria including citation checks and source matches.

    Args:
        case: The TestCase schema.
        output: String response from target.
        sources: List of returned sources or None.

    Returns:
        A tuple containing:
          - A list of RAG-specific AssertionResult schemas.
          - A source match score (float, 0.0 to 1.0).
          - A hallucination risk flag (bool).
    """
    assertions: list[AssertionResult] = []
    returned_sources = sources or []

    # 1. Citation Required Check
    if case.citation_required:
        success = len(returned_sources) > 0
        assertions.append(
            AssertionResult(
                name="citation_required",
                success=success,
                expected="At least one source citation",
                actual=f"{len(returned_sources)} sources returned",
                reason=None if success else "Response required citation but no sources were returned.",
            )
        )

    # 2. Expected Sources matching
    source_match_score = 1.0
    has_expected_sources = len(case.expected_sources) > 0

    if has_expected_sources:
        matched_count = 0
        missing_sources = []

        for expected in case.expected_sources:
            found = False
            for returned in returned_sources:
                if expected.lower() in returned.lower():
                    found = True
                    break
            if found:
                matched_count += 1
            else:
                missing_sources.append(expected)

        source_match_score = matched_count / len(case.expected_sources)
        success = matched_count == len(case.expected_sources)

        assertions.append(
            AssertionResult(
                name="expected_sources",
                success=success,
                expected=str(case.expected_sources),
                actual=str(returned_sources),
                reason=None if success else f"Expected sources list missing elements: {missing_sources}",
            )
        )

    # 3. Fact containment checks
    # Treat 'expected_contains' items as required facts.
    facts_failed = False
    if case.expected_contains:
        for fact in case.expected_contains:
            if fact.lower() not in output.lower():
                facts_failed = True
                break

    # Hallucination Risk Heuristics
    # Flag high risk if expected citations are empty, source_match_score is low (< 0.5),
    # or the answer failed to output the expected contains facts.
    hallucination_risk = False
    if case.citation_required and not returned_sources:
        hallucination_risk = True
    elif has_expected_sources and source_match_score < 0.5:
        hallucination_risk = True
    elif facts_failed:
        hallucination_risk = True

    return assertions, source_match_score, hallucination_risk
