# r3po

r3po scans public GitHub and GitLab repositories for dependency CVEs (Trivy), leaked secrets (Gitleaks), and SAST issues (Semgrep). It provides one Docker image containing a CLI, FastAPI API, and React dashboard.

## Run

```bash
docker build -t r3po .
docker run --rm -p 8000:8000 r3po
```

Open `http://localhost:8000`. The browser and API share the same origin: FastAPI serves the compiled React files and `/scan` from port 8000, so production needs no CORS configuration.

## CLI usage

r3po's scanning engine depends on three external tools that cannot be bundled via pip: Trivy, Gitleaks, and Semgrep. Install them once per machine, then the CLI itself is a single command.

1. Install the three scanning tools (one-time, per machine):

   - Trivy: [https://trivy.dev/latest/getting-started/installation/](https://trivy.dev/latest/getting-started/installation/)
   - Gitleaks: [https://github.com/gitleaks/gitleaks#installing](https://github.com/gitleaks/gitleaks#installing)
   - Semgrep: `pip install semgrep`

2. Install r3po:

   ```bash
   git clone https://github.com/Arielpoghon/r3po.git
   cd r3po
   pip install -e .
   ```

> **Note:** on distributions that enforce PEP 668 (Arch, recent Debian/Ubuntu), a plain `pip install -e .` will fail with `externally-managed-environment`. Use a virtual environment first:
>
> ```bash
> python -m venv .venv
> source .venv/bin/activate
> pip install -e .
> ```

3. Run it:

   ```bash
   r3po scan https://github.com/digininja/DVWA
   ```

For a zero-install experience (no local tool setup at all), use the hosted web dashboard instead: [https://r3po.onrender.com/](https://r3po.onrender.com/)

## Architecture

`core.scanner.scan()` is the only scan engine. It validates the public GitHub/GitLab URL, performs a depth-one clone in a temporary directory, enforces a 200MB clone limit, invokes Trivy/Gitleaks/Semgrep sequentially, and aggregates their normalized `Finding` objects into one `ScanReport`. The CLI and FastAPI endpoint both call that function.

## Limits and future work

- **Public repositories only.** No authentication or token support — private repos are out of scope for this version.
- **Single scan at a time.** No job queue or background workers; a second scan request while one is running returns HTTP 429. No scan history or persistence — every scan is stateless and its cloned data is deleted immediately after.
- **200MB clone size limit and 180-second global timeout.** Large repositories may be rejected or return partial results with `scan_timed_out: true`.
- **Sequential tool execution.** Trivy, Gitleaks, and Semgrep run one after another rather than in parallel, to stay within free-tier hosting memory limits (512MB RAM on Render).
- **No result deduplication or cross-tool correlation.** Findings are returned as reported by each underlying tool.

Planned but not built: async job queue with progress polling, private-repo support via access tokens, parallel tool execution for self-hosted/paid deployments, scan history persistence.

## Render

Connect this repository as a Docker Web Service on Render's free tier, leaving build/start overrides empty. The Dockerfile starts the app. Add the resulting public URL here after deployment. Free instances sleep after about 15 minutes of inactivity, so warm it before a presentation.
