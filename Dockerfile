FROM node:20 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ARG TRIVY_VERSION=0.74.0
ARG GITLEAKS_VERSION=8.30.0
RUN apt-get update && apt-get install -y --no-install-recommends git curl ca-certificates tar && rm -rf /var/lib/apt/lists/* \
 && curl -fsSL "https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz" | tar -xz -C /usr/local/bin trivy \
 && curl -fsSL -o /tmp/gitleaks.tar.gz "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz" \
 && tar -xzf /tmp/gitleaks.tar.gz -C /usr/local/bin gitleaks && rm /tmp/gitleaks.tar.gz
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && trivy --version && gitleaks version && semgrep --version
COPY core/ core/
COPY cli/ cli/
COPY backend/ backend/
COPY --from=frontend-build /app/frontend/dist frontend/dist
EXPOSE 8000
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
