#!/usr/bin/env bash
set -euo pipefail

TARGET_DOMAIN="clauseguard.alpfrtech.com"
ORIGINAL_DEMO_DOMAIN="app.alpfrtech.com"

echo "============================================================"
echo "ClauseGuard AI - Production Ingress & Health Verification"
echo "Target Endpoint: https://${TARGET_DOMAIN}"
echo "============================================================"

# 1. Pods Status
echo "[1/5] Checking ClauseGuard AI Pods in default namespace..."
kubectl get pods -n default -l app=clauseguard-ai -o wide
echo "✔ Pods reported"

# 2. Ingress Status
echo ""
echo "[2/5] Checking Kubernetes Ingress resources..."
kubectl get ingress -n default
echo "✔ Ingress verified"

# 3. Test /healthz
echo ""
echo "[3/5] Testing HTTPS Health Probe (https://${TARGET_DOMAIN}/healthz)..."
HEALTH_RES=$(curl -fsSL --retry 3 --retry-delay 2 "https://${TARGET_DOMAIN}/healthz")
echo "  Response: ${HEALTH_RES}"
if echo "${HEALTH_RES}" | grep -q "ClauseGuard AI"; then
  echo "✔ /healthz returned healthy ClauseGuard status"
else
  echo "✖ /healthz did not return expected payload"
  exit 1
fi

# 4. Test /api/samples
echo ""
echo "[4/5] Testing Contract Sample API (https://${TARGET_DOMAIN}/api/samples)..."
SAMPLE_RES=$(curl -fsSL --retry 3 --retry-delay 2 "https://${TARGET_DOMAIN}/api/samples")
if echo "${SAMPLE_RES}" | grep -q "freelance_msa"; then
  echo "✔ /api/samples loaded pre-packaged contract catalog successfully"
else
  echo "✖ /api/samples failed"
  exit 1
fi

# 4b. Test Export Report API
echo ""
echo "[4b/5] Testing 1-Click Report Export API (https://${TARGET_DOMAIN}/api/export/markdown)..."
EXPORT_RES=$(curl -fsSL -X POST --retry 3 --retry-delay 2 "https://${TARGET_DOMAIN}/api/export/markdown" \
  -H "Content-Type: application/json" \
  -d '{"analysis": {"filename": "test_contract.txt", "risk_summary": {"score": 85, "grade": "Low Risk", "metrics": {}}, "findings": []}}')
if echo "${EXPORT_RES}" | grep -q "ClauseGuard AI — Executive Contract Risk Audit Report"; then
  echo "✔ /api/export/markdown generated valid executive audit report"
else
  echo "✖ /api/export/markdown failed"
  exit 1
fi

# 5. Regression Check on original demo app
echo ""
echo "[5/5] Regression check: Verifying original demo microservice (https://${ORIGINAL_DEMO_DOMAIN})..."
DEMO_RES=$(curl -fsSL --retry 3 --retry-delay 2 "https://${ORIGINAL_DEMO_DOMAIN}/")
echo "  Response: ${DEMO_RES}"
if echo "${DEMO_RES}" | grep -q "Hello from Kubernetes"; then
  echo "✔ Regression check passed: original demo microservice untouched"
else
  echo "✖ Demo microservice regression detected"
  exit 1
fi

echo ""
echo "============================================================"
echo "✔ ALL VERIFICATION CHECKS PASSED SUCCESSFULLY!"
echo "ClauseGuard AI Dashboard: https://${TARGET_DOMAIN}"
echo "Original Demo Microservice: https://${ORIGINAL_DEMO_DOMAIN}"
echo "============================================================"
