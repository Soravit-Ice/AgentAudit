import pytest
from pydantic import ValidationError

from agentaudit.models import TargetConfig, TestCase, TestSuite


def test_valid_target_config() -> None:
    # Test typical configurations
    cfg = TargetConfig(type="mock")
    assert cfg.type == "mock"

    cfg_http = TargetConfig(
        type="http",
        url="http://localhost:8000/chat",
        headers={"Content-Type": "application/json"},
        input_key="prompt",
        output_key="response",
    )
    assert cfg_http.type == "http"
    assert cfg_http.url == "http://localhost:8000/chat"
    assert cfg_http.input_key == "prompt"


def test_invalid_target_config() -> None:
    # Test invalid literal types
    with pytest.raises(ValidationError):
        TargetConfig(type="invalid_type")  # type: ignore


def test_valid_test_case() -> None:
    case = TestCase(
        id="test-1",
        input="Hello",
        expected_contains=["hi", "there"],
        must_not_contain=["bye"],
        expected_policy="refuse",
        max_latency_ms=250,
    )
    assert case.id == "test-1"
    assert "hi" in case.expected_contains
    assert case.expected_policy == "refuse"
    assert case.max_latency_ms == 250


def test_test_suite_validation() -> None:
    suite_data = {
        "name": "basic-test-suite",
        "description": "Checking parser",
        "target": {
            "type": "mock",
        },
        "cases": [
            {
                "id": "case-1",
                "input": "Prompt here",
                "expected_contains": ["Expected result"],
            }
        ],
    }

    suite = TestSuite.model_validate(suite_data)
    assert suite.name == "basic-test-suite"
    assert len(suite.cases) == 1
    assert suite.cases[0].id == "case-1"
