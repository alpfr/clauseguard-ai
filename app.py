"""
ClauseGuard AI - Intelligent Contract & Legal Risk Analysis Application
FastAPI Server Entrypoint with static UI hosting and Kubernetes probes.
"""

import logging
import os
import socket
import re
from typing import Optional, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.document_parser import parse_document, parse_text
from services.analyzer import analyze_contract
from services.sample_contracts import SAMPLE_CONTRACTS
from services.chat_assistant import answer_contract_question
from services.report_generator import (
    generate_markdown_report,
    generate_html_report,
    generate_summary_text,
)
from services.diff_engine import compute_word_diff

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("clauseguard.main")

app = FastAPI(
    title="ClauseGuard AI",
    description="Automated Legal Risk Auditing, Clause Intelligence & Contract Assistant",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class AnalyzeTextRequest(BaseModel):
    text: str
    filename: Optional[str] = "contract.txt"
    api_key: Optional[str] = None


class ChatRequest(BaseModel):
    question: str
    contract_text: str
    api_key: Optional[str] = None


# ------------------------------------------------------------------------------
# Kubernetes Probes
# ------------------------------------------------------------------------------
@app.get("/healthz")
async def health_check():
    """Kubernetes liveness and readiness probe endpoint."""
    return {"status": "ok", "app": "ClauseGuard AI", "version": "2.0.0"}


@app.get("/api/info")
async def system_info():
    """Cluster node and instance identification."""
    hostname = socket.gethostname()
    return {
        "status": "running",
        "pod": hostname,
        "product": "ClauseGuard AI",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "Production")
    }


# ------------------------------------------------------------------------------
# Sample Contracts API
# ------------------------------------------------------------------------------
@app.get("/api/samples")
async def get_samples():
    """Return pre-packaged realistic contracts for instant 1-click demos."""
    items = {}
    for key, data in SAMPLE_CONTRACTS.items():
        items[key] = {
            "title": data["title"],
            "category": data["category"],
            "description": data["description"],
            "preview": data["text"][:300] + "..."
        }
    return items


@app.get("/api/samples/{sample_id}")
async def get_sample_detail(sample_id: str):
    """Retrieve full text of a selected sample contract."""
    if sample_id not in SAMPLE_CONTRACTS:
        raise HTTPException(status_code=404, detail="Sample contract not found")
    data = SAMPLE_CONTRACTS[sample_id]
    return {
        "id": sample_id,
        "title": data["title"],
        "category": data["category"],
        "description": data["description"],
        "text": data["text"]
    }


# ------------------------------------------------------------------------------
# Analysis Engine Endpoints
# ------------------------------------------------------------------------------
@app.post("/api/analyze/upload")
async def analyze_file_upload(
    file: UploadFile = File(...),
    api_key: Optional[str] = Form(None)
):
    """Upload PDF, DOCX, or TXT file and run risk analysis."""
    try:
        content = await file.read()
        filename = file.filename or "uploaded_contract.pdf"
        parsed = parse_document(content, filename)
        text = parsed["full_text"]

        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract readable text from document.")

        analysis = analyze_contract(text, filename=filename, api_key=api_key)
        analysis["document_meta"] = {
            "total_pages": parsed["total_pages"],
            "char_count": parsed["char_count"],
            "format": parsed["format"]
        }
        analysis["extracted_text"] = text
        return JSONResponse(content=analysis)
    except Exception as exc:
        logger.error("Error processing file upload: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/analyze/text")
async def analyze_raw_text(payload: AnalyzeTextRequest):
    """Analyze pasted contract text directly."""
    if not payload.text or not payload.text.strip():
        raise HTTPException(status_code=400, detail="Contract text is required.")

    analysis = analyze_contract(payload.text, filename=payload.filename or "agreement.txt", api_key=payload.api_key)
    analysis["document_meta"] = {
        "total_pages": max(1, len(payload.text) // 2500),
        "char_count": len(payload.text),
        "format": "text"
    }
    analysis["extracted_text"] = payload.text
    return JSONResponse(content=analysis)


# ------------------------------------------------------------------------------
# Conversational Assistant API
# ------------------------------------------------------------------------------
@app.post("/api/chat")
async def chat_with_contract(payload: ChatRequest):
    """Ask questions against contract context."""
    if not payload.question.strip() or not payload.contract_text.strip():
        raise HTTPException(status_code=400, detail="Question and contract text are required.")

    response = answer_contract_question(
        question=payload.question,
        contract_text=payload.contract_text,
        api_key=payload.api_key
    )
    return JSONResponse(content=response)


# ------------------------------------------------------------------------------
# Export & Reporting API
# ------------------------------------------------------------------------------
class ExportRequest(BaseModel):
    analysis: Dict[str, Any]


@app.post("/api/export/markdown")
async def export_markdown(payload: ExportRequest):
    """Generate and return Markdown audit report as a downloadable attachment."""
    try:
        md_text = generate_markdown_report(payload.analysis)
        filename = payload.analysis.get("filename", "agreement")
        clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', filename).replace(".txt", "").replace(".pdf", "").replace(".docx", "")
        export_filename = f"{clean_name}_ClauseGuard_Audit.md"
        headers = {
            "Content-Disposition": f'attachment; filename="{export_filename}"'
        }
        return Response(content=md_text, media_type="text/markdown; charset=utf-8", headers=headers)
    except Exception as exc:
        logger.error("Error generating markdown report: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/export/html")
async def export_html(payload: ExportRequest):
    """Generate and return standalone executive HTML audit report for printing or PDF saving."""
    try:
        html_content = generate_html_report(payload.analysis)
        return HTMLResponse(content=html_content)
    except Exception as exc:
        logger.error("Error generating HTML report: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/export/summary")
async def export_summary(payload: ExportRequest):
    """Return compact executive audit summary for clipboard or email."""
    try:
        summary_text = generate_summary_text(payload.analysis)
        return JSONResponse(content={"summary": summary_text})
    except Exception as exc:
        logger.error("Error generating summary: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ------------------------------------------------------------------------------
# Visual Redline & Diff API
# ------------------------------------------------------------------------------
class DiffRequest(BaseModel):
    original: str
    proposed: str


@app.post("/api/diff")
async def get_clause_diff(payload: DiffRequest):
    """Compute word-level diff between original clause and proposed counter-language."""
    diff_data = compute_word_diff(payload.original, payload.proposed)
    return JSONResponse(content=diff_data)


# ------------------------------------------------------------------------------
# Root SPA Page
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the ClauseGuard AI single page application."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>ClauseGuard AI Backend Ready</h1><p>Static index.html not yet built.</p>")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
