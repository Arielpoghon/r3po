"""Trivy filesystem scan adapter."""

from __future__ import annotations

import json
import subprocess

from core.schema import Finding


def _severity(value: str | None) -> str:
    value = (value or "info").lower()
    return value if value in {"critical", "high", "medium", "low", "info"} else "info"


def run(repo_path: str, timeout: float = 120) -> list[Finding]:
    completed = subprocess.run(
        ["trivy", "fs", "--format", "json", "--quiet", repo_path],
        capture_output=True, text=True, timeout=max(timeout, 1), check=False,
    )
    if completed.returncode not in (0,):
        raise RuntimeError(completed.stderr.strip() or "trivy exited with an error")
    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError("trivy returned invalid JSON") from exc

    findings: list[Finding] = []
    for result in payload.get("Results", []):
        target = result.get("Target", "")
        for vulnerability in result.get("Vulnerabilities") or []:
            findings.append(Finding(
                tool="trivy", severity=_severity(vulnerability.get("Severity")), file=target,
                title=vulnerability.get("VulnerabilityID", "Trivy vulnerability"),
                description=vulnerability.get("Description") or vulnerability.get("Title") or "Vulnerability found by Trivy.",
                remediation=vulnerability.get("FixedVersion") and f"Upgrade to {vulnerability['FixedVersion']}.",
            ))
    return findings
