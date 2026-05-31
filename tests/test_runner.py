import os
import tempfile

import pytest
import yaml

from agentaudit.exceptions import ConfigurationError
from agentaudit.models import TestSuite
from agentaudit.runner import load_test_suite, run_suite


def test_load_test_suite_success() -> None:
    suite_data = {
        "name": "temp-suite",
        "description": "temp",
        "target": {"type": "mock"},
        "cases": [{"id": "case-1", "input": "ขอคืนสินค้าได้ภายในกี่วัน"}],
    }

    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False, encoding="utf-8") as temp_file:
        yaml.dump(suite_data, temp_file, default_flow_style=False)
        temp_path = temp_file.name

    try:
        suite = load_test_suite(temp_path)
        assert isinstance(suite, TestSuite)
        assert suite.name == "temp-suite"
        assert len(suite.cases) == 1
    finally:
        os.remove(temp_path)


def test_load_test_suite_invalid() -> None:
    # Invalid YAML syntax
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False, encoding="utf-8") as temp_file:
        temp_file.write("invalid: yaml: : syntax")
        temp_path = temp_file.name

    try:
        with pytest.raises(ConfigurationError):
            load_test_suite(temp_path)
    finally:
        os.remove(temp_path)


@pytest.mark.asyncio
async def test_run_suite_mock() -> None:
    suite = TestSuite(
        name="test-run",
        target={"type": "mock"},
        cases=[
            {
                "id": "case-1",
                "input": "ขอคืนสินค้าได้ภายในกี่วัน",
                "expected_contains": ["7 วัน"],
                "expected_sources": ["refund_policy.md"],
            }
        ],
    )

    result = await run_suite(suite)
    assert result.name == "test-run"
    assert result.total_cases == 1
    assert result.passed == 1
    assert result.status == "PASSED"
    assert result.accuracy == 100.0
    assert result.average_latency > 0.0

    # Verify case sub-items
    case_res = result.results[0]
    assert case_res.id == "case-1"
    assert case_res.success is True
    assert case_res.sources == ["refund_policy.md"]
