"""
ClauseGuard AI - Automated Test Suite for Perspective-Aware Negotiation Agent
Tests:
1. /api/perspectives endpoint
2. Posture score inversion: Vendor vs Buyer vs Balanced
3. Tactical negotiation email script generation
4. Counter-proposal adaptation
5. Report generation posture integration
"""

import pytest
from fastapi.testclient import TestClient

from app import app
from services.sample_contracts import SAMPLE_CONTRACTS
from services.analyzer import analyze_contract
from services.perspective_engine import (
    POSTURE_METADATA,
    apply_perspective,
    recalculate_score_for_posture,
)
import services.report_generator as rg


@pytest.fixture
def client():
    return TestClient(app)


def test_api_perspectives_endpoint(client):
    """Ensure /api/perspectives returns metadata for all supported postures."""
    resp = client.get("/api/perspectives")
    assert resp.status_code == 200
    data = resp.json()
    assert "vendor" in data
    assert "buyer" in data
    assert "balanced" in data
    assert data["vendor"]["title"] == "Service Provider / Vendor"
    assert data["buyer"]["title"] == "Enterprise Buyer / Client"
    assert data["balanced"]["title"] == "Balanced / Commercial Standard"


def test_posture_score_inversion_freelance_msa():
    """
    In a contractor-hostile freelance agreement,
    the Vendor posture must flag extreme risk (>= 75),
    whereas the Buyer posture must recognize buyer-favorable terms (<= 45).
    """
    msa_text = SAMPLE_CONTRACTS["freelance_msa"]["text"]
    
    vendor_analysis = analyze_contract(msa_text, filename="freelance_msa.txt", posture="vendor")
    buyer_analysis = analyze_contract(msa_text, filename="freelance_msa.txt", posture="buyer")
    balanced_analysis = analyze_contract(msa_text, filename="freelance_msa.txt", posture="balanced")

    vendor_score = vendor_analysis["risk_summary"]["score"]
    buyer_score = buyer_analysis["risk_summary"]["score"]
    balanced_score = balanced_analysis["risk_summary"]["score"]

    # Verify score relationship
    assert vendor_score >= 75, f"Expected high risk for vendor, got {vendor_score}"
    assert buyer_score <= 45, f"Expected low/moderate risk for buyer, got {buyer_score}"
    assert buyer_score < balanced_score <= vendor_score

    # Check posture info
    assert vendor_analysis["posture_info"]["posture"] == "vendor"
    assert buyer_analysis["posture_info"]["posture"] == "buyer"
    assert balanced_analysis["posture_info"]["posture"] == "balanced"


def test_negotiation_scripts_generated_for_vendor():
    """Ensure flagged high/critical findings in vendor mode have tactical email scripts."""
    msa_text = SAMPLE_CONTRACTS["freelance_msa"]["text"]
    analysis = analyze_contract(msa_text, filename="msa.txt", posture="vendor")
    findings = analysis["findings"]

    scripts_found = [f for f in findings if f.get("negotiation_script")]
    assert len(scripts_found) >= 2, "Expected at least 2 findings with tactical negotiation email scripts"

    for f in scripts_found:
        script = f["negotiation_script"]
        assert len(script.strip()) > 30
        assert any(k in script.lower() for k in ["policy", "insurance", "indemnification", "redlined", "reviewed", "fees", "covenant", "notice", "clause", "payment"])


def test_analyze_api_with_posture(client):
    """Test /api/analyze/text passes posture through to analysis response."""
    sample = SAMPLE_CONTRACTS["freelance_msa"]
    
    # Test Buyer Posture
    resp_buyer = client.post("/api/analyze/text", json={
        "text": sample["text"],
        "filename": "buyer_test.txt",
        "posture": "buyer"
    })
    assert resp_buyer.status_code == 200
    data_buyer = resp_buyer.json()
    assert data_buyer["posture_info"]["posture"] == "buyer"
    assert "Enterprise Buyer" in data_buyer["posture_info"]["title"]

    # Test Vendor Posture
    resp_vendor = client.post("/api/analyze/text", json={
        "text": sample["text"],
        "filename": "vendor_test.txt",
        "posture": "vendor"
    })
    assert resp_vendor.status_code == 200
    data_vendor = resp_vendor.json()
    assert data_vendor["posture_info"]["posture"] == "vendor"
    assert data_vendor["risk_summary"]["score"] > data_buyer["risk_summary"]["score"]


def test_reports_contain_posture_and_scripts():
    """Verify generated Markdown and HTML reports embed posture and negotiation scripts."""
    msa_text = SAMPLE_CONTRACTS["freelance_msa"]["text"]
    analysis = analyze_contract(msa_text, filename="freelance_msa.txt", posture="vendor")
    analysis["document_meta"] = {"char_count": len(msa_text), "total_pages": 3, "format": "text"}

    md_report = rg.generate_markdown_report(analysis)
    assert "Audit Posture / Perspective" in md_report
    assert "Service Provider / Vendor" in md_report
    assert "Tactical Negotiation Email Script" in md_report

    html_report = rg.generate_html_report(analysis)
    assert "Active Audit Perspective & Negotiation Posture" in html_report
    assert "Tactical Negotiation Email Script" in html_report
    assert "posture-badge" in html_report
