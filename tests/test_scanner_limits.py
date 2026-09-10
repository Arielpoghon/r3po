import subprocess
from unittest.mock import Mock, patch

from core.scanner import MAX_CLONE_SIZE_BYTES, scan


def test_invalid_url_is_rejected_without_clone():
    with patch("core.scanner.subprocess.run") as command:
        report = scan("https://example.com/owner/repo")
    assert report.error and "Invalid repository URL" in report.error
    command.assert_not_called()


def test_oversize_clone_is_rejected():
    with patch("core.scanner.subprocess.run", return_value=Mock()), patch(
        "core.scanner._directory_size_bytes", return_value=MAX_CLONE_SIZE_BYTES + 1
    ):
        report = scan("https://github.com/owner/repo")
    assert report.error == "Repository exceeds the 200MB scan limit."


def test_tool_timeout_returns_partial_result():
    with patch("core.scanner.subprocess.run", return_value=Mock()), patch(
        "core.scanner._directory_size_bytes", return_value=1
    ), patch("core.scanner.trivy_runner.run", side_effect=subprocess.TimeoutExpired("trivy", 1)):
        report = scan("https://github.com/owner/repo")
    assert report.scan_timed_out is True
