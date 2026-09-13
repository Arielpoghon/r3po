"""Combine normalized tool findings into the shared report."""

from pathlib import Path
from urllib.parse import quote

from core.schema import Finding, ScanReport

_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def build_source_url(repo_url: str, commit_sha: str, absolute_file_path: str,
                     clone_root: str, line: int | None) -> str | None:
    """Build an immutable GitHub/GitLab source URL for a cloned finding."""
    normalized_repo_url = repo_url.rstrip("/")
    if normalized_repo_url.endswith(".git"):
        normalized_repo_url = normalized_repo_url[:-4]
    if "github.com" in normalized_repo_url:
        source_prefix = f"{normalized_repo_url}/blob/{commit_sha}"
    elif "gitlab.com" in normalized_repo_url:
        source_prefix = f"{normalized_repo_url}/-/blob/{commit_sha}"
    else:
        return None

    relative_path = absolute_file_path.lstrip("/")
    is_within_clone = False
    if absolute_file_path:
        try:
            relative_path = Path(absolute_file_path).resolve().relative_to(Path(clone_root).resolve()).as_posix()
            is_within_clone = True
        except ValueError:
            # Some tools return a manifest path (for example, go.mod) rather
            # than an absolute checkout path. It is already repo-relative.
            relative_path = absolute_file_path.lstrip("/")

    source_url = f"{source_prefix}/{quote(relative_path, safe='/')}"
    return f"{source_url}#L{line}" if is_within_clone and line is not None else source_url


def aggregate(repo_url: str, *finding_lists: list[Finding], tool_errors: list[str] | None = None,
              error: str | None = None, scan_timed_out: bool = False,
              commit_sha: str | None = None, clone_root: str | None = None) -> ScanReport:
    findings = [finding for finding_list in finding_lists for finding in finding_list]
    if commit_sha and clone_root:
        findings = [finding.model_copy(update={"source_url": build_source_url(
            repo_url, commit_sha, finding.file, clone_root, finding.line
        )}) for finding in findings]
    findings.sort(key=lambda finding: (_ORDER[finding.severity], finding.file, finding.line or 0))
    return ScanReport(repo_url=repo_url, findings=findings, tool_errors=tool_errors or [],
                      error=error, scan_timed_out=scan_timed_out, commit_sha=commit_sha)
