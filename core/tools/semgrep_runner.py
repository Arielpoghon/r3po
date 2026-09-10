"""Semgrep SAST adapter."""

from __future__ import annotations

import json
import subprocess

from core.schema import Finding


def _severity(value: str | None) -> str:
    value = (value or "info").lower()
    return value if value in {"critical", "high", "medium", "low", "info"} else "info"


def run(repo_path: str, timeout: float = 120) -> list[Finding]:
    completed = subprocess.run(
        ["semgrep", "--config=auto", "--json", "--quiet", repo_path],
        capture_output=True, text=True, timeout=max(timeout, 1), check=False,
    )
    # Semgrep uses 1 for findings in some versions.
    if completed.returncode not in (0, 1):
        raise RuntimeError(completed.stderr.strip() or "semgrep exited with an error")
    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError("semgrep returned invalid JSON") from exc

    findings: list[Finding] = []
    for result in payload.get("results", []):
        extra = result.get("extra", {})
        metadata = extra.get("metadata", {})
        findings.append(Finding(
            tool="semgrep", severity=_severity(extra.get("severity")), file=result.get("path", ""),
            line=result.get("start", {}).get("line"), title=result.get("check_id", "Semgrep finding"),
            description=extra.get("message", "SAST finding reported by Semgrep."),
            remediation=metadata.get("remediation") or metadata.get("fix"),
        ))
    return findings
