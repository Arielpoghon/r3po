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

3. Run it:

   ```bash
   r3po scan https://github.com/digininja/DVWA
   ```

For a zero-install experience (no local tool setup at all), use the hosted web dashboard instead: [https://r3po.onrender.com/](https://r3po.onrender.com/)

## Architecture

`core.scanner.scan()` is the only scan engine. It validates the public GitHub/GitLab URL, performs a depth-one clone in a temporary directory, enforces a 200MB clone limit, invokes Trivy/Gitleaks/Semgrep sequentially, and aggregates their normalized `Finding` objects into one `ScanReport`. The CLI and FastAPI endpoint both call that function.

## Limits and future work

Only public GitHub/GitLab repositories are supported. Scans have a 200MB checkout cap and a default 180-second global timeout. Tool failures are reported without discarding other findings. The hosted single-container service accepts one scan at a time; concurrent requests receive HTTP 429. Future work: an async job queue. There are no accounts, persistence, private-repo tokens, batch scans, CI integration, or Kubernetes deployment.

## Render

Connect this repository as a Docker Web Service on Render's free tier, leaving build/start overrides empty. The Dockerfile starts the app. Add the resulting public URL here after deployment. Free instances sleep after about 15 minutes of inactivity, so warm it before a presentation.
