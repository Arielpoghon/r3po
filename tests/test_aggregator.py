from core.aggregator import aggregate
from core.schema import Finding


def test_aggregate_sorts_severity_and_preserves_contract():
    report = aggregate("https://github.com/example/project",
        [Finding(tool="semgrep", severity="low", file="app.py", line=2, title="x", description="x")],
        [Finding(tool="trivy", severity="critical", file="requirements.txt", title="CVE-x", description="x")],
    )
    assert [finding.severity for finding in report.findings] == ["critical", "low"]
    assert report.model_dump()["repo_url"] == "https://github.com/example/project"
