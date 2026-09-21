# Contributing to ClauseGuard AI

Thank you for your interest in contributing to **ClauseGuard AI**! This guide covers our development workflow, coding standards, testing procedures, and deployment guidelines.

---

## 1. Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/alpfr/clauseguard-ai.git
   cd clauseguard-ai
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pytest httpx
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```
   Navigate to `http://localhost:8080`.

---

## 2. Running Automated Tests

All pull requests and code changes must pass the automated test suite:

```bash
env PYTHONPATH=. pytest tests/ -v
```

### Adding New Tests
- Place report export tests in [`tests/test_exports.py`](file:///Users/alpfr/Downloads/scripts/clauseguard-ai/tests/test_exports.py).
- Place redline and diff tests in [`tests/test_diff.py`](file:///Users/alpfr/Downloads/scripts/clauseguard-ai/tests/test_diff.py).

---

## 3. Adding New Risk Heuristics

To contribute a new legal risk detection rule:
1. Open [`services/analyzer.py`](file:///Users/alpfr/Downloads/scripts/clauseguard-ai/services/analyzer.py).
2. Locate `evaluate_rules(text: str)`.
3. Add a regex or pattern-matching heuristic returning:
   ```python
   {
       "id": "unique-rule-id",
       "category": "Contract Category",
       "severity": "critical" | "high" | "warning" | "favorable",
       "title": "Clear Plain-English Title",
       "clause_excerpt": matched_text,
       "explanation": "Why this term creates risk or exposure.",
       "counter_proposal": "Suggested counter-language to propose in negotiations.",
       "section": "Relevant Section"
   }
   ```
4. Add unit test coverage in `tests/` verifying the heuristic matches hostile clauses and ignores balanced ones.

---

## 4. Kubernetes Deployment

To deploy updates to the production AWS EKS cluster:

```bash
# Authenticate, build amd64 container, push to ECR, and execute rolling update
./scripts/deploy-k8s.sh

# Run the 5-step automated health and regression verification probe
./scripts/verify-k8s.sh
```

---

## 5. Coding Standards

- **PEP 8**: Follow standard Python conventions.
- **Typing**: Use standard type annotations (`typing.Dict`, `typing.List`, `typing.Optional`).
- **Security**: Never commit API keys or sensitive credentials. All secrets should be passed via environment variables or the client UI settings modal.
- **Non-Root**: Ensure the Dockerfile maintains execution under non-root system user `appuser` (UID 10001).
