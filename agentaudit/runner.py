import asyncio
import datetime
import os
import time

import yaml
from typing import Literal

from agentaudit.adapters import get_adapter
from agentaudit.adapters.base import BaseAdapter
from agentaudit.exceptions import ConfigurationError
from agentaudit.models import AssertionResult, CaseResult, SuiteResult, TestCase, TestSuite
from agentaudit.rag.evaluator import evaluate_rag
from agentaudit.safety.detectors import detect_pii_leak, detect_system_prompt_leak
from agentaudit.scoring import evaluate_assertions


def load_test_suite(filepath: str) -> TestSuite:
    """Loads and validates a single TestSuite from a YAML file.

    Args:
        filepath: Absolute or relative path to the YAML file.

    Returns:
        Validated TestSuite model.

    Raises:
        ConfigurationError: If parsing or validation fails.
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ConfigurationError(f"YAML file '{filepath}' must contain a key-value dictionary structure.")

        return TestSuite.model_validate(data)
    except Exception as e:
        raise ConfigurationError(f"Failed to load and validate test suite from '{filepath}': {e}") from e


def load_suites_from_path(path: str) -> list[TestSuite]:
    """Recursively crawls a path to load and validate all YAML suites.

    Args:
        path: File or directory path.

    Returns:
        List of loaded TestSuite models.

    Raises:
        ConfigurationError: If paths are invalid.
    """
    if os.path.isfile(path):
        return [load_test_suite(path)]
    elif os.path.isdir(path):
        suites = []
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith((".yml", ".yaml")):
                    full_path = os.path.join(root, file)
                    suites.append(load_test_suite(full_path))
        return suites
    else:
        raise ConfigurationError(f"Target path '{path}' does not exist.")


async def run_case(adapter: BaseAdapter, case: TestCase) -> CaseResult:
    """Executes a single test case using the adapter and scores the outcome.

    Args:
        adapter: Loaded target adapter.
        case: The TestCase being tested.

    Returns:
        CaseResult recording all outputs, metrics, and assertions.
    """
    is_safety_case = (
        case.metadata.get("is_safety_case", False)
        or case.expected_policy is not None
        or "safety" in case.id.lower()
    )

    try:
        output_text, sources, latency_ms = await adapter.execute(case.input)

        # 1. Evaluate standard assertions
        assertions = evaluate_assertions(case, output_text, latency_ms)

        # 2. Evaluate RAG-specific assertions
        rag_assertions, source_match_score, hallucination_risk = evaluate_rag(
            case, output_text, sources
        )
        assertions.extend(rag_assertions)

        # 3. Post-hoc safety detectors (PII & System instruction indicator checks)
        pii_leaks = detect_pii_leak(output_text)
        prompt_leaks = detect_system_prompt_leak(output_text)

        if pii_leaks:
            assertions.append(
                AssertionResult(
                    name="safety_detector:no_pii_leak",
                    success=False,
                    expected="Response must be clear of PII leaks",
                    actual=f"Detected leaks: {pii_leaks}",
                    reason=f"Defensive scanner intercepted confidential info leakage: {pii_leaks}",
                )
            )

        if prompt_leaks:
            assertions.append(
                AssertionResult(
                    name="safety_detector:no_system_prompt_leak",
                    success=False,
                    expected="Response must be clear of system instructions",
                    actual=f"Detected leaks: {prompt_leaks}",
                    reason=f"Defensive scanner intercepted prompt leakage indicators: {prompt_leaks}",
                )
            )

        total_assertions = len(assertions)
        passed_assertions = sum(1 for a in assertions if a.success)
        success = (passed_assertions == total_assertions) if total_assertions > 0 else True
        score = (passed_assertions / total_assertions) if total_assertions > 0 else 1.0

        return CaseResult(
            id=case.id,
            input=case.input,
            output=output_text,
            success=success,
            score=score,
            latency_ms=latency_ms,
            assertions=assertions,
            sources=sources,
            hallucination_risk=hallucination_risk,
            is_safety_case=is_safety_case,
        )

    except Exception as e:
        # Gracefully capture exceptions without crashing the full suite run
        return CaseResult(
            id=case.id,
            input=case.input,
            output=f"Execution error: {e}",
            success=False,
            score=0.0,
            latency_ms=0.0,
            assertions=[
                AssertionResult(
                    name="adapter_execution",
                    success=False,
                    expected="Successful target execution",
                    actual="Raised exception",
                    reason=str(e),
                )
            ],
            sources=None,
            hallucination_risk=True,
            is_safety_case=is_safety_case,
        )


async def run_suite(suite: TestSuite) -> SuiteResult:
    """Runs a full suite of test cases concurrently and aggregates final results.

    Args:
        suite: Loaded TestSuite model.

    Returns:
        SuiteResult summarizing the test run.
    """
    start_time_dt = datetime.datetime.now(datetime.UTC)
    start_time_str = start_time_dt.isoformat()
    start_perf = time.perf_counter()

    adapter = get_adapter(suite.target)

    # Execute all cases concurrently using asyncio
    tasks = [run_case(adapter, case) for case in suite.cases]
    results = await asyncio.gather(*tasks)

    duration_seconds = time.perf_counter() - start_perf
    end_time_str = datetime.datetime.now(datetime.UTC).isoformat()

    total_cases = len(results)
    passed = sum(1 for r in results if r.success)
    failed = total_cases - passed
    accuracy = (passed / total_cases * 100.0) if total_cases > 0 else 100.0

    # Aggregate safety metrics
    safety_cases = [r for r in results if r.is_safety_case]
    if safety_cases:
        passed_safety = sum(1 for r in safety_cases if r.success)
        safety_score = (passed_safety / len(safety_cases)) * 100.0
    else:
        safety_score = None

    # Calculate average latency
    total_latency = sum(r.latency_ms for r in results)
    average_latency = (total_latency / total_cases) if total_cases > 0 else 0.0

    status: Literal["PASSED", "FAILED"] = "PASSED" if passed == total_cases else "FAILED"

    return SuiteResult(
        name=suite.name,
        description=suite.description,
        target_type=suite.target.type,
        total_cases=total_cases,
        passed=passed,
        failed=failed,
        accuracy=accuracy,
        safety_score=safety_score,
        average_latency=average_latency,
        status=status,
        start_time=start_time_str,
        end_time=end_time_str,
        duration_seconds=duration_seconds,
        results=results,
    )
