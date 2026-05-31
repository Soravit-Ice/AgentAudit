from typing import Any, Literal

from pydantic import BaseModel, Field


class TargetConfig(BaseModel):
    type: Literal["mock", "http", "command"]
    url: str | None = None
    method: Literal["GET", "POST"] = "POST"
    headers: dict[str, str] = Field(default_factory=dict)
    input_key: str = "input"
    output_key: str = "output"
    sources_key: str = "sources"
    command: str | None = None


class TestCase(BaseModel):
    __test__ = False
    id: str
    input: str
    expected_contains: list[str] = Field(default_factory=list)
    must_not_contain: list[str] = Field(default_factory=list)
    exact_match: str | None = None
    regex_match: list[str] = Field(default_factory=list)
    expected_policy: Literal["allow", "refuse"] | None = None
    expected_sources: list[str] = Field(default_factory=list)
    citation_required: bool = False
    max_latency_ms: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TestSuite(BaseModel):
    __test__ = False
    name: str
    description: str = ""
    target: TargetConfig
    cases: list[TestCase] = Field(default_factory=list)


class AssertionResult(BaseModel):
    name: str
    success: bool
    expected: Any
    actual: Any
    reason: str | None = None


class CaseResult(BaseModel):
    id: str
    input: str
    output: str
    success: bool
    score: float  # Fraction of passed assertions (0.0 to 1.0)
    latency_ms: float
    assertions: list[AssertionResult] = Field(default_factory=list)
    sources: list[str] | None = None
    hallucination_risk: bool = False
    is_safety_case: bool = False


class SuiteResult(BaseModel):
    name: str
    description: str = ""
    target_type: Literal["mock", "http", "command"]
    total_cases: int
    passed: int
    failed: int
    accuracy: float  # passed / total * 100
    safety_score: float | None = None  # passed safety / total safety * 100 (None if no safety cases)
    average_latency: float  # in ms
    status: Literal["PASSED", "FAILED"]
    start_time: str
    end_time: str
    duration_seconds: float
    results: list[CaseResult] = Field(default_factory=list)


class RunConfig(BaseModel):
    output_dir: str = "reports"
    format: Literal["json", "md", "html", "all"] = "all"
    fail_on_risk: Literal["low", "medium", "high", "none"] = "none"
    fail_under_score: float = 0.8
    verbose: bool = False
    quiet: bool = False
