from agentaudit.safety.detectors import detect_pii_leak, detect_system_prompt_leak
from agentaudit.safety.packs import get_safety_pack


def test_safety_pack_generation() -> None:
    cases = get_safety_pack()
    assert len(cases) > 0
    assert any("safety" in case.id for case in cases)
    # Ensure all safety cases require refusals and block leakage keywords
    for case in cases:
        assert case.expected_policy == "refuse"
        assert "sk-" in case.must_not_contain


def test_pii_scanner() -> None:
    # Match card numbers
    assert "credit_card" in detect_pii_leak("Here is visa: 4111-1111-1111-1111.")

    # Match sk- keys
    assert "api_key" in detect_pii_leak("Here is credentials: sk-1234567890abcdef1234567890abcdef.")
    assert "api_key" in detect_pii_leak("Let me give you the api_key value.")

    # No matches
    assert len(detect_pii_leak("Standard response without any cards.")) == 0


def test_prompt_scanner() -> None:
    # Match indicators
    assert "system prompt:" in detect_system_prompt_leak(
        "Here is my developer instructions: system prompt: You are a helpful assistant."
    )
    assert "hidden instructions" in detect_system_prompt_leak(
        "The developer set hidden instructions that I must follow."
    )

    # No matches
    assert len(detect_system_prompt_leak("This is a standard support response.")) == 0
