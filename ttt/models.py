"""
Shared data models for the Telecom Test Toolkit ecosystem.

All tools produce and consume these models as their data contracts,
enabling seamless data flow between pipeline stages.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class TestResult:
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
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "status": self.status,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp,
            "source_tool": self.source_tool,
            "message": self.message,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TestResult":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class AnalysisResult:
    """Aggregated analysis output from a single tool run.

    Produced by log analyzers (testwatch, log_analyzer, testscope).
    """
    tool_name: str
    total_events: int = 0
    passed: int = 0
    failed: int = 0
    success_rate: float = 0.0
    results: List[TestResult] = field(default_factory=list)
    kpis: Dict[str, Any] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    raw_summary: str = ""

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "total_events": self.total_events,
            "passed": self.passed,
            "failed": self.failed,
            "success_rate": self.success_rate,
            "results": [r.to_dict() for r in self.results],
            "kpis": self.kpis,
            "issues": self.issues,
            "raw_summary": self.raw_summary,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisResult":
        results_data = data.pop("results", [])
        obj = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        obj.results = [TestResult.from_dict(r) for r in results_data]
        return obj


@dataclass
class FlakinessReport:
    """Output from the flakiness scorer tool.

    Categorizes each test case by stability diagnosis.
    """
    test_id: str
    diagnosis: str  # "Stable", "High (Flaky)", "Recent Hard Fail", etc.
    builds_analyzed: int = 0
    transitions: int = 0
    last_status: str = ""

    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "diagnosis": self.diagnosis,
            "builds_analyzed": self.builds_analyzed,
            "transitions": self.transitions,
            "last_status": self.last_status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FlakinessReport":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class PipelineOutput:
    """Complete output from a full pipeline run.

    Aggregates results from all tools into a single object.
    """
    run_id: str
    timestamp: str = ""
    log_files: List[str] = field(default_factory=list)
    analyses: List[AnalysisResult] = field(default_factory=list)
    flakiness_reports: List[FlakinessReport] = field(default_factory=list)
    report_path: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "log_files": self.log_files,
            "analyses": [a.to_dict() for a in self.analyses],
            "flakiness_reports": [f.to_dict() for f in self.flakiness_reports],
            "report_path": self.report_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PipelineOutput":
        analyses_data = data.pop("analyses", [])
        flakiness_data = data.pop("flakiness_reports", [])
        obj = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        obj.analyses = [AnalysisResult.from_dict(a) for a in analyses_data]
        obj.flakiness_reports = [FlakinessReport.from_dict(f) for f in flakiness_data]
        return obj
