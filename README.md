# ClauseGuard AI - Intelligent Contract Risk Auditing & Legal Intelligence SaaS

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**ClauseGuard AI** is a modern B2B and prosumer contract intelligence SaaS application. It allows business owners, founders, consultants, freelancers, and procurement teams to instantly audit agreements, detect hidden legal risks, compute 0–100 risk scores, and negotiate favorable counter-clauses with a single click.

---

## Key Features

1. **Multi-Format Ingestion**:
   - Supports multi-page **PDF**, **DOCX**, **TXT**, and **Markdown** agreements with page-level indexing.
2. **Dynamic 0–100 Risk Score Radial Gauge**:
   - Automated risk evaluation mapped to standardized severity tiers (Critical, High, Moderate, Low Risk).
3. **Classified Red-Flag Audit Across 18 Risk Vectors**:
   - Detects uncapped indemnification, unilateral termination, $100 nominal liability caps, overly broad non-competes, and auto-renewal traps.
   - For every flagged issue, provides the verbatim clause excerpt, plain-English legal risk explanation, and a ready-to-copy counter-clause.
4. **Interactive Contract Assistant ("Ask My Contract")**:
   - Context-grounded Q&A assistant providing natural-language answers with exact clause citations and tactical negotiation advice.
5. **1-Click Real-World Sample Demos**:
   - Pre-packaged real-world contracts for instant testing without uploading files (Freelance MSA, Mutual NDA, Commercial Lease).
6. **Dual-Engine Architecture**:
   - **Autonomous Engine**: Fully functional out-of-the-box with zero API key setup.
   - **External LLM Integration**: Optionally configure OpenAI or Gemini API keys in the UI settings for deep generative legal reasoning.

---

## Architecture & Project Structure

```
clauseguard-ai/
├── app.py                     # FastAPI application server & route handlers
├── services/                  # Core intelligence and parsing services
│   ├── __init__.py
│   ├── analyzer.py            # 18-category risk matrix & dual-engine analyzer
│   ├── chat_assistant.py      # Context-grounded conversational Q&A assistant
│   ├── document_parser.py     # Multi-page PDF, text, and markdown parser
│   └── sample_contracts.py    # Pre-packaged real-world contracts for 1-click demos
├── static/                    # Single-page responsive web frontend
│   ├── index.html             # Dashboard with SVG risk gauge and chat panel
│   ├── css/styles.css         # Modern dark mode & glassmorphism design system
│   └── js/app.js              # Client-side file dropzone, gauge animation, and chat UI
├── Dockerfile                 # Hardened, non-root (UID 10001) container build
├── requirements.txt           # Python dependencies (FastAPI, Uvicorn, PyPDF, etc.)
└── .dockerignore              # Docker build exclusions
```

---

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.11+
- Virtual environment tool (`venv` or `uv`)

### 2. Setup & Installation
```bash
# Clone or navigate to the repository
cd clauseguard-ai

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the development server
python app.py
```
Open [http://localhost:8080](http://localhost:8080) in your web browser.

---

## Docker Deployment

Build and run the production-grade, non-root container:

```bash
# Build the image
docker build -t clauseguard-ai:latest .

# Run the container
docker run -d -p 8080:8080 --name clauseguard clauseguard-ai:latest

# Access the app
curl http://localhost:8080/healthz
```

## Kubernetes & AWS Production Deployment

ClauseGuard AI is deployed to Amazon EKS Auto Mode behind an AWS Network Load Balancer (NLB) with Ingress NGINX and Route 53 DNS.

- **Live Production URL**: [https://clauseguard.alpfrtech.com](https://clauseguard.alpfrtech.com)
- **Health Check Endpoint**: [https://clauseguard.alpfrtech.com/healthz](https://clauseguard.alpfrtech.com/healthz)

### Kubernetes Manifests (`k8s/`)

| File | Resource | Description |
| :--- | :--- | :--- |
| [`k8s/deployment.yaml`](file:///Users/alpfr/Downloads/scripts/clauseguard-ai/k8s/deployment.yaml) | `Deployment` | 2 replicas, non-root user (UID 10001), rolling update, `/healthz` liveness & readiness probes. |
| [`k8s/service.yaml`](file:///Users/alpfr/Downloads/scripts/clauseguard-ai/k8s/service.yaml) | `Service` | ClusterIP service exposing port 8080. |
| [`k8s/network-policy.yaml`](file:///Users/alpfr/Downloads/scripts/clauseguard-ai/k8s/network-policy.yaml) | `NetworkPolicy` | Zero-Trust isolation restricting ingress port 8080 traffic to Ingress NGINX pods only. |
| [`k8s/ingress.yaml`](file:///Users/alpfr/Downloads/scripts/clauseguard-ai/k8s/ingress.yaml) | `Ingress` | NGINX ingress routing `clauseguard.alpfrtech.com` with rate limiting and 10MB upload limits. |

### Automated Deploy & Verification Scripts

```bash
# 1. Build amd64 image, push to ECR, and apply Kubernetes manifests
./scripts/deploy-k8s.sh

# 2. Run automated 5-step health, ingress, and regression verification probe
./scripts/verify-k8s.sh
```

---

## API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| **`/healthz`** | `GET` | Health check endpoint for container orchestrators (Kubernetes / ECS). |
| **`/api/info`** | `GET` | System version and instance identification. |
| **`/api/samples`** | `GET` | Returns list of pre-packaged contract demos. |
| **`/api/samples/{id}`** | `GET` | Returns full text of a selected demo contract. |
| **`/api/analyze/upload`** | `POST` | Multipart file upload (PDF/TXT) with complete risk audit response. |
| **`/api/analyze/text`** | `POST` | JSON payload analysis of raw contract text. |
| **`/api/chat`** | `POST` | Context-grounded contract Q&A assistant. |
| **`/api/export/markdown`** | `POST` | Generates and downloads GitHub-flavored Markdown audit report. |
| **`/api/export/html`** | `POST` | Renders standalone executive-grade printable HTML report for PDF export. |
| **`/api/export/summary`** | `POST` | Returns concise executive summary for clipboard copying or email briefing. |

---

## License

MIT License. Free for commercial and private use.

