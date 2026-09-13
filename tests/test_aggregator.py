from core.aggregator import aggregate, build_source_url
from core.schema import Finding


def test_aggregate_sorts_severity_and_preserves_contract():
    report = aggregate("https://github.com/example/project",
        [Finding(tool="semgrep", severity="low", file="app.py", line=2, title="x", description="x")],
        [Finding(tool="trivy", severity="critical", file="requirements.txt", title="CVE-x", description="x")],
    )
    assert [finding.severity for finding in report.findings] == ["critical", "low"]
    assert report.model_dump()["repo_url"] == "https://github.com/example/project"


def test_build_source_url_for_github_file_and_line():
    assert build_source_url(
        "https://github.com/example/project", "abc123", "/tmp/r3po/repo/src/app.py", "/tmp/r3po/repo", 42
    ) == "https://github.com/example/project/blob/abc123/src/app.py#L42"


def test_build_source_url_for_gitlab_manifest_without_line():
    assert build_source_url(
        "https://gitlab.com/example/project", "abc123", "go.mod", "/tmp/r3po/repo", None
    ) == "https://gitlab.com/example/project/-/blob/abc123/go.mod"
