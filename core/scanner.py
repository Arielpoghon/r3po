"""Bounded, sequential repository scan orchestration."""

from __future__ import annotations

import re
import subprocess
import tempfile
import time
from pathlib import Path

from core.aggregator import aggregate
from core.schema import ScanReport
from core.tools import gitleaks_runner, semgrep_runner, trivy_runner

MAX_CLONE_SIZE_BYTES = 200 * 1024 * 1024
PUBLIC_REPO_URL = re.compile(r"^https://(?:github\.com|gitlab\.com)/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?$")


def _directory_size_bytes(path: str) -> int:
    result = subprocess.run(["du", "-sb", path], capture_output=True, text=True, check=True)
    return int(result.stdout.split()[0])


def _remaining(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise subprocess.TimeoutExpired("scan", 0)
    return remaining


def scan(repo_url: str, timeout_sec: int = 180) -> ScanReport:
    """Scan a public GitHub/GitLab repository, always removing its temporary clone."""
    if not PUBLIC_REPO_URL.fullmatch(repo_url):
        return ScanReport(repo_url=repo_url, error="Invalid repository URL: use a public https://github.com/<owner>/<repo> or https://gitlab.com/<owner>/<repo> URL.")
    if timeout_sec <= 0:
        return ScanReport(repo_url=repo_url, error="timeout_sec must be greater than zero.")

    deadline = time.monotonic() + timeout_sec
    tool_errors: list[str] = []
    outputs = []
    with tempfile.TemporaryDirectory(prefix="r3po-") as temporary_directory:
        checkout = str(Path(temporary_directory) / "repo")
        try:
            subprocess.run(["git", "clone", "--depth", "1", repo_url, checkout], capture_output=True,
                           text=True, timeout=_remaining(deadline), check=True)
        except subprocess.TimeoutExpired:
            return aggregate(repo_url, tool_errors=tool_errors, scan_timed_out=True)
        except subprocess.CalledProcessError as exc:
            return aggregate(repo_url, tool_errors=tool_errors,
                             error=f"Could not clone repository: {exc.stderr.strip() or 'git clone failed.'}")

        try:
            commit_sha = subprocess.run(["git", "-C", checkout, "rev-parse", "HEAD"], capture_output=True,
                                        text=True, timeout=_remaining(deadline), check=True).stdout.strip()
        except subprocess.TimeoutExpired:
            return aggregate(repo_url, tool_errors=tool_errors, scan_timed_out=True)
        except subprocess.CalledProcessError as exc:
            return aggregate(repo_url, tool_errors=tool_errors,
                             error=f"Could not resolve cloned commit: {exc.stderr.strip() or 'git rev-parse failed.'}")

        if _directory_size_bytes(checkout) > MAX_CLONE_SIZE_BYTES:
            return aggregate(repo_url, tool_errors=tool_errors, commit_sha=commit_sha,
                             error="Repository exceeds the 200MB scan limit.")

        # Sequential execution deliberately limits memory use on small Render instances.
        for tool_name, runner in (("trivy", trivy_runner.run), ("gitleaks", gitleaks_runner.run), ("semgrep", semgrep_runner.run)):
            try:
                outputs.append(runner(checkout, timeout=_remaining(deadline)))
            except subprocess.TimeoutExpired:
                return aggregate(repo_url, *outputs, tool_errors=tool_errors, scan_timed_out=True,
                                 commit_sha=commit_sha, clone_root=checkout)
            except Exception as exc:  # An unavailable/crashed scanner must not cancel other scans.
                tool_errors.append(f"{tool_name}: {exc}")
        timed_out = time.monotonic() >= deadline
        return aggregate(repo_url, *outputs, tool_errors=tool_errors, scan_timed_out=timed_out,
                         commit_sha=commit_sha, clone_root=checkout)
