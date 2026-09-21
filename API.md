# ClauseGuard AI — REST API Integration Guide

This guide details all available REST endpoints exposed by **ClauseGuard AI**, including sample `curl` requests, request payloads, and response structures.

- **Base URL (Production)**: `https://clauseguard.alpfrtech.com`
- **Base URL (Local)**: `http://localhost:8080`

---

## 1. Health & System

### `GET /healthz`
Kubernetes liveness and readiness probe endpoint.

```bash
curl -fsSL https://clauseguard.alpfrtech.com/healthz
```

**Response (`200 OK`)**:
```json
{
  "status": "ok",
  "app": "ClauseGuard AI",
  "version": "2.0.0"
}
```

---

### `GET /api/info`
Returns pod hostname, active environment, and service version.

```bash
curl -fsSL https://clauseguard.alpfrtech.com/api/info
```

**Response (`200 OK`)**:
```json
{
  "status": "running",
  "pod": "clauseguard-ai-775cdbc658-6xg87",
  "product": "ClauseGuard AI",
  "version": "2.0.0",
  "environment": "Production"
}
```

---

## 2. Sample Contract Catalog

### `GET /api/samples`
Retrieve catalog of pre-packaged contract demos.

```bash
curl -fsSL https://clauseguard.alpfrtech.com/api/samples
```

**Response (`200 OK`)**:
```json
{
  "freelance_msa": {
    "title": "Freelance Master Services Agreement (High Risk)",
    "category": "Critical Risk (Score: 98)",
    "description": "Uncapped indemnification, $100 total liability cap, and aggressive 3-year non-compete.",
    "preview": "MASTER SERVICES AGREEMENT\nThis Agreement is entered into..."
  },
  "mutual_nda": {
    "title": "Mutual Non-Disclosure Agreement",
    "category": "Low Risk (Score: 18)",
    "description": "Standard 2-year bilateral confidentiality with standard trade secret protections.",
    "preview": "MUTUAL NONDISCLOSURE AGREEMENT\nThis Mutual Non-Disclosure Agreement..."
  },
  "commercial_lease": {
    "title": "Commercial Triple-Net Office Lease",
    "category": "Moderate Risk (Score: 54)",
    "description": "Pass-through operating expenses (CAM), strict alteration surrender clauses.",
    "preview": "STANDARD COMMERCIAL LEASE AGREEMENT\nThis Lease is made as of..."
  }
}
```

---

## 3. Contract Risk Analysis

### `POST /api/analyze/text`
Analyze raw contract text across 18 legal risk vectors.

```bash
curl -fsSL -X POST https://clauseguard.alpfrtech.com/api/analyze/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contractor shall indemnify Client against all claims without limitation. Contractor agrees to a non-compete for 5 years worldwide. Payment terms are Net 120 days.",
    "filename": "consulting_agreement.txt"
  }'
```

**Response (`200 OK`)**:
```json
{
  "filename": "consulting_agreement.txt",
  "metadata": {
    "contract_type": "Commercial Agreement",
    "parties": ["Disclosing Party", "Receiving Party"],
    "governing_law": "Not specified",
    "term": "Not specified",
    "liability_cap_status": "Unknown"
  },
  "risk_summary": {
    "score": 60,
    "grade": "Moderate / High Risk",
    "badge_color": "amber",
    "recommendation": "Contains unfavorable clauses that need redlining prior to execution, particularly payment terms and liability boundaries.",
    "metrics": {
      "critical_flags": 1,
      "high_flags": 1,
      "warnings": 0,
      "favorable_clauses": 0,
      "total_audited": 2
    }
  },
  "findings": [
    {
      "id": "indemnity-uncapped",
      "category": "Indemnification & Liability",
      "severity": "critical",
      "title": "Uncapped & Asymmetrical Indemnification",
      "clause_excerpt": "Contractor shall indemnify Client against all claims without limitation.",
      "explanation": "You are agreeing to defend and indemnify the other party without any financial cap or mutual protection.",
      "counter_proposal": "Replace with mutual indemnification capped at total fees paid under the agreement in the prior 12 months, strictly limited to third-party direct claims arising from gross negligence.",
      "section": "Indemnification Section",
      "diff": {
        "words_removed": 6,
        "words_added": 23,
        "left_html": "<del class=\"diff-del\">Contractor shall indemnify Client against all claims without limitation.</del>",
        "right_html": "<ins class=\"diff-ins\">Replace with mutual indemnification capped at total fees paid under the agreement in the prior 12 months, strictly limited to third-party direct claims arising from gross negligence.</ins>",
        "unified_html": "<del class=\"diff-del\">...</del><ins class=\"diff-ins\">...</ins>"
      }
    }
  ],
  "char_count": 164,
  "analyzer_engine": "ClauseGuard Autonomous Legal Engine v3.0"
}
```

---

## 4. Visual Redline & Diff Engine

### `POST /api/diff`
Compute tokenized word-level diffs and legal mark-up between two clauses.

```bash
curl -fsSL -X POST https://clauseguard.alpfrtech.com/api/diff \
  -H "Content-Type: application/json" \
  -d '{
    "original": "Contractor shall indemnify Client for all damages without limit.",
    "proposed": "Each party shall indemnify the other capped at fees paid in prior 12 months."
  }'
```

**Response (`200 OK`)**:
```json
{
  "original_raw": "Contractor shall indemnify Client for all damages without limit.",
  "proposed_raw": "Each party shall indemnify the other capped at fees paid in prior 12 months.",
  "left_html": "<del class=\"diff-del\" title=\"Removed / Replaced\">Contractor</del> shall indemnify <del class=\"diff-del\" title=\"Removed / Replaced\">Client for all damages without limit</del>.",
  "right_html": "<ins class=\"diff-ins\" title=\"Protective Counter-Proposal\">Each party</ins> shall indemnify <ins class=\"diff-ins\" title=\"Protective Counter-Proposal\">the other capped at fees paid in prior 12 months</ins>.",
  "unified_html": "<del class=\"diff-del\">Contractor</del><ins class=\"diff-ins\">Each party</ins> shall indemnify <del class=\"diff-del\">Client for all damages without limit</del><ins class=\"diff-ins\">the other capped at fees paid in prior 12 months</ins>.",
  "stats": {
    "words_removed": 6,
    "words_added": 12,
    "words_unchanged": 2,
    "change_percentage": 90.0
  }
}
```

---

## 5. Executive Report Export

### `POST /api/export/markdown`
Download complete audit as a formatted `.md` attachment.

```bash
curl -fsSL -X POST https://clauseguard.alpfrtech.com/api/export/markdown \
  -H "Content-Type: application/json" \
  -d '{"analysis": { ... }}' \
  --output audit_report.md
```

---

### `POST /api/export/html`
Render standalone executive HTML document with print stylesheets.

```bash
curl -fsSL -X POST https://clauseguard.alpfrtech.com/api/export/html \
  -H "Content-Type: application/json" \
  -d '{"analysis": { ... }}' \
  --output audit_report.html
```

---

### `POST /api/export/summary`
Returns concise executive summary string for clipboard or email.

```bash
curl -fsSL -X POST https://clauseguard.alpfrtech.com/api/export/summary \
  -H "Content-Type: application/json" \
  -d '{"analysis": { ... }}'
```

**Response (`200 OK`)**:
```json
{
  "summary": "🛡️ ClauseGuard AI Audit Summary: consulting_agreement.txt\nRisk Score: 60/100 (Moderate / High Risk)\nCritical Flags: 1 | High Flags: 1 | Warnings: 0\n\nKey Areas of Concern:\n- [CRITICAL] Uncapped & Asymmetrical Indemnification\n\nAudited at: https://clauseguard.alpfrtech.com"
}
```

---

## 6. Conversational Assistant

### `POST /api/chat`
Ask natural-language questions grounded in the contract text.

```bash
curl -fsSL -X POST https://clauseguard.alpfrtech.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What happens if I terminate this agreement early?",
    "contract_text": "Either party may terminate upon 30 days prior written notice."
  }'
```

**Response (`200 OK`)**:
```json
{
  "answer": "Either party has the right to terminate the agreement early by delivering 30 days prior written notice.",
  "citations": ["Either party may terminate upon 30 days prior written notice."],
  "confidence": "high"
}
```
