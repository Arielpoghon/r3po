"""Gitleaks secret-detection adapter."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile

from core.schema import Finding


def run(repo_path: str, timeout: float = 120) -> list[Finding]:
    fd, report_path = tempfile.mkstemp(suffix="-gitleaks.json")
    os.close(fd)
    try:
        completed = subprocess.run(
            ["gitleaks", "detect", "--no-git", "--source", repo_path, "--report-format", "json", "--report-path", report_path],
            capture_output=True, text=True, timeout=max(timeout, 1), check=False,
        )
        # Gitleaks exits 1 when leaks are found, so report content is authoritative.
        try:
            with open(report_path, encoding="utf-8") as report_file:
                payload = json.load(report_file)
        except (OSError, json.JSONDecodeError) as exc:
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or "gitleaks exited with an error") from exc
            raise RuntimeError("gitleaks did not produce valid JSON") from exc
    finally:
        try:
            os.unlink(report_path)
        except FileNotFoundError:
            pass

    return [Finding(
        tool="gitleaks", severity="high", file=item.get("File", ""), line=item.get("StartLine"),
        title=item.get("RuleID", "Potential secret"),
        description=item.get("Description") or "Potential secret found by Gitleaks.",
        remediation="Remove the secret, rotate it, and load it from a secret manager.",
    ) for item in payload]
