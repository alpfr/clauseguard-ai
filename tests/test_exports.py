"""
ClauseGuard AI - Automated Test Suite for Report Generation & Export Endpoints
"""

import pytest
from fastapi.testclient import TestClient

from app import app
from services.sample_contracts import SAMPLE_CONTRACTS
from services.analyzer import analyze_contract
import services.report_generator as rg


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_analysis():
    sample = SAMPLE_CONTRACTS["freelance_msa"]
    analysis = analyze_contract(sample["text"], filename="freelance_msa.txt")
    analysis["document_meta"] = {
        "char_count": len(sample["text"]),
        "total_pages": 3,
        "format": "text"
    }
    return analysis


def test_health_check(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "ClauseGuard AI"


def test_markdown_generator_direct(sample_analysis):
    md = rg.generate_markdown_report(sample_analysis)
    assert "ClauseGuard AI — Executive Contract Risk Audit Report" in md
    assert "Executive Summary & Risk Score" in md
    assert "Detailed Audit Findings & Counter-Proposals" in md
    assert "freelance_msa.txt" in md


def test_html_generator_direct(sample_analysis):
    html = rg.generate_html_report(sample_analysis)
    assert "<!DOCTYPE html>" in html
    assert "Executive Contract Risk Audit" in html
    assert "@media print" in html
    assert "freelance_msa.txt" in html


def test_summary_generator_direct(sample_analysis):
    summary = rg.generate_summary_text(sample_analysis)
    assert "ClauseGuard AI Audit Summary" in summary
    assert "Risk Score" in summary


def test_export_markdown_api(client, sample_analysis):
    response = client.post("/api/export/markdown", json={"analysis": sample_analysis})
    assert response.status_code == 200
    assert "attachment" in response.headers.get("content-disposition", "")
    assert "freelance_msa_ClauseGuard_Audit.md" in response.headers.get("content-disposition", "")
    assert "ClauseGuard AI" in response.text


def test_export_html_api(client, sample_analysis):
    response = client.post("/api/export/html", json={"analysis": sample_analysis})
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "Executive Contract Risk Audit" in response.text


def test_export_summary_api(client, sample_analysis):
    response = client.post("/api/export/summary", json={"analysis": sample_analysis})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "ClauseGuard AI Audit Summary" in data["summary"]
