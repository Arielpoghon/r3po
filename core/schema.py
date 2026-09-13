"""The one report contract used by every r3po interface."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["critical", "high", "medium", "low", "info"]


class Finding(BaseModel):
    tool: Literal["trivy", "gitleaks", "semgrep"]
    severity: Severity
    file: str
    line: int | None = None
    title: str
    description: str
    remediation: str | None = None
    source_url: str | None = None


class ScanReport(BaseModel):
    repo_url: str
    commit_sha: str | None = None
    findings: list[Finding] = Field(default_factory=list)
    tool_errors: list[str] = Field(default_factory=list)
    error: str | None = None
    scan_timed_out: bool = False
