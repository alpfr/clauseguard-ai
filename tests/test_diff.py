"""
ClauseGuard AI - Visual Redline & Diff Engine Tests
"""

import pytest
from fastapi.testclient import TestClient

from app import app
from services.diff_engine import tokenize, compute_word_diff
from services.analyzer import analyze_contract
from services.sample_contracts import SAMPLE_CONTRACTS


@pytest.fixture
def client():
    return TestClient(app)


def test_tokenization():
    text = "Contractor shall indemnify, defend, and hold harmless Client."
    tokens = tokenize(text)
    assert len(tokens) > 0
    assert "".join(tokens) == text
    assert "Contractor" in tokens
    assert "," in tokens
    assert "." in tokens


def test_compute_word_diff_identical():
    text = "Governing law shall be New York."
    diff = compute_word_diff(text, text)
    assert diff["stats"]["words_removed"] == 0
    assert diff["stats"]["words_added"] == 0
    assert diff["stats"]["change_percentage"] == 0.0
    assert "<del" not in diff["left_html"]
    assert "<ins" not in diff["right_html"]


def test_compute_word_diff_replacement():
    original = "Contractor agrees to unlimited liability for all damages."
    proposed = "Contractor liability shall be capped at fees paid in prior 12 months."

    diff = compute_word_diff(original, proposed)
    assert diff["stats"]["words_removed"] > 0
    assert diff["stats"]["words_added"] > 0
    assert "<del class=\"diff-del\"" in diff["left_html"]
    assert "<ins class=\"diff-ins\"" in diff["right_html"]
    assert "<del" in diff["unified_html"] and "<ins" in diff["unified_html"]


def test_diff_api_endpoint(client):
    payload = {
        "original": "Client may terminate at will without notice.",
        "proposed": "Either party may terminate upon 30 days written notice."
    }
    response = client.post("/api/diff", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "left_html" in data
    assert "right_html" in data
    assert "unified_html" in data
    assert "stats" in data
    assert data["stats"]["words_removed"] > 0
    assert data["stats"]["words_added"] > 0


def test_analyzer_findings_enriched_with_diff():
    sample = SAMPLE_CONTRACTS["freelance_msa"]
    result = analyze_contract(sample["text"], filename="freelance.txt")

    findings = result.get("findings", [])
    assert len(findings) > 0

    for finding in findings:
        if finding.get("counter_proposal"):
            assert "diff" in finding
            diff = finding["diff"]
            assert "left_html" in diff
            assert "right_html" in diff
            assert "unified_html" in diff
            assert "stats" in diff
