from agentaudit.models import TestCase
from agentaudit.scoring import check_refusal, evaluate_assertions


def test_refusal_heuristics_english() -> None:
    # Match various refusal sentences
    assert check_refusal("I cannot assist with that request.") is True
    assert check_refusal("I'm unable to reveal developer details.") is True
    assert check_refusal("Sorry, I can't help with that.") is True
    assert check_refusal("I am an AI, so I cannot perform administrative operations.") is True

    # Standard sentences should not match
    assert check_refusal("Sure, I can help you with that!") is False
    assert check_refusal("The refund policy takes 7 days.") is False


def test_refusal_heuristics_thai() -> None:
    # Match Thai refusal sentences
    assert check_refusal("ขออภัยด้วยค่ะ ฉันไม่สามารถให้ข้อมูลลูกค้าท่านอื่นได้") is True
    assert check_refusal("ไม่ควรทำสิ่งนี้") is True
    assert check_refusal("ไม่ได้รับอนุญาตให้เปิดเผย") is True

    # Standard Thai sentences
    assert check_refusal("คุณสามารถขอคืนเงินได้ภายใน 7 วันทำการ") is False


def test_exact_match_scoring() -> None:
    case = TestCase(id="exact-check", input="Prompt", exact_match="Expected Text")

    # Correct output
    results = evaluate_assertions(case, "Expected Text", 10.0)
    assert len(results) == 1
    assert results[0].success is True

    # Inexact output
    results_fail = evaluate_assertions(case, "Different Text", 10.0)
    assert len(results_fail) == 1
    assert results_fail[0].success is False


def test_contains_and_exclusions() -> None:
    case = TestCase(
        id="sub-check",
        input="Prompt",
        expected_contains=["valid", "text"],
        must_not_contain=["forbidden", "unsafe"],
    )

    # Completely successful case
    results = evaluate_assertions(case, "This valid text is great", 10.0)
    assert len(results) == 4  # 2 contains + 2 must_not_contain
    assert all(r.success for r in results)

    # Missing expected contains
    results_fail_contains = evaluate_assertions(case, "This text is great", 10.0)
    # expected_contains:valid should fail
    failures = [r for r in results_fail_contains if not r.success]
    assert len(failures) == 1
    assert "valid" in failures[0].name

    # Containing forbidden words
    results_fail_forbidden = evaluate_assertions(case, "This valid text is unsafe", 10.0)
    failures_forbidden = [r for r in results_fail_forbidden if not r.success]
    assert len(failures_forbidden) == 1
    assert "unsafe" in failures_forbidden[0].name


def test_regex_scoring() -> None:
    case = TestCase(
        id="regex-check",
        input="Prompt",
        regex_match=[r"^Order #[0-9]{4}$"],
    )

    # Match
    results = evaluate_assertions(case, "Order #1234", 15.0)
    assert len(results) == 1
    assert results[0].success is True

    # No match
    results_fail = evaluate_assertions(case, "Order #ABC", 15.0)
    assert len(results_fail) == 1
    assert results_fail[0].success is False


def test_expected_policy_scoring() -> None:
    case_refuse = TestCase(id="policy-refuse", input="Prompt", expected_policy="refuse")

    # Success: bot refuses
    results = evaluate_assertions(case_refuse, "I cannot help with that.", 10.0)
    assert len(results) == 1
    assert results[0].success is True

    # Fail: bot compiles
    results_fail = evaluate_assertions(case_refuse, "Here is the customer data.", 10.0)
    assert len(results_fail) == 1
    assert results_fail[0].success is False


def test_latency_scoring() -> None:
    case = TestCase(id="latency-check", input="Prompt", max_latency_ms=100)

    # Fast
    results = evaluate_assertions(case, "Ok", 45.0)
    assert len(results) == 1
    assert results[0].success is True

    # Slow
    results_fail = evaluate_assertions(case, "Ok", 120.0)
    assert len(results_fail) == 1
    assert results_fail[0].success is False
