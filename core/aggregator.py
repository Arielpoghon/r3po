"""Combine normalized tool findings into the shared report."""

from core.schema import Finding, ScanReport

_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def aggregate(repo_url: str, *finding_lists: list[Finding], tool_errors: list[str] | None = None,
              error: str | None = None, scan_timed_out: bool = False) -> ScanReport:
    findings = [finding for finding_list in finding_lists for finding in finding_list]
    findings.sort(key=lambda finding: (_ORDER[finding.severity], finding.file, finding.line or 0))
    return ScanReport(repo_url=repo_url, findings=findings, tool_errors=tool_errors or [],
                      error=error, scan_timed_out=scan_timed_out)
