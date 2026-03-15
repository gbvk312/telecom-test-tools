"""
Shared data models for the Telecom Test Toolkit ecosystem.

All tools produce and consume these models as their data contracts,
enabling seamless data flow between pipeline stages.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any


class TestResult(BaseModel):
    """A single test result from any analysis tool.

    This is the universal data contract — every tool that analyzes logs
    should produce a list of TestResult objects.
    """

    test_id: str
    status: str  # "pass", "fail", "skip", "error", "running"
    duration_seconds: Optional[float] = None
    timestamp: Optional[str] = None
    source_tool: str = ""
    message: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "TestResult":
        return cls.model_validate(data)


class AnalysisResult(BaseModel):
    """Aggregated analysis output from a single tool run.

    Produced by log analyzers (testwatch, log_analyzer, testscope).
    """

    tool_name: str
    total_events: int = 0
    passed: int = 0
    failed: int = 0
    success_rate: float = 0.0
    results: List[TestResult] = Field(default_factory=list)
    kpis: Dict[str, Any] = Field(default_factory=dict)
    issues: List[str] = Field(default_factory=list)
    raw_summary: str = ""

    model_config = ConfigDict(from_attributes=True)

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisResult":
        return cls.model_validate(data)


class FlakinessReport(BaseModel):
    """Output from the flakiness scorer tool.

    Categorizes each test case by stability diagnosis.
    """

    test_id: str
    diagnosis: str  # "Stable", "High (Flaky)", "Recent Hard Fail", etc.
    builds_analyzed: int = 0
    transitions: int = 0
    last_status: str = ""

    model_config = ConfigDict(from_attributes=True)

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "FlakinessReport":
        return cls.model_validate(data)


class PipelineOutput(BaseModel):
    """Complete output from a full pipeline run.

    Aggregates results from all tools into a single object.
    """

    run_id: str
    timestamp: str = ""
    log_files: List[str] = Field(default_factory=list)
    analyses: List[AnalysisResult] = Field(default_factory=list)
    flakiness_reports: List[FlakinessReport] = Field(default_factory=list)
    report_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "PipelineOutput":
        return cls.model_validate(data)
