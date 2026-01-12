from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List, Dict
import uuid
import asyncio
from datetime import datetime
from urllib.parse import urlparse
import logging

from scanners.headers import check_security_headers
from scanners.ssl_check import check_ssl_tls
from scanners.xss import check_xss
from scanners.sqli import check_sql_injection
from scanners.info_disclosure import check_info_disclosure
from models import ScanRequest, ScanStatus, ScanResult, Finding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VulnScan API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for scans (in production, use a database)
scans: Dict[str, ScanResult] = {}

# Demo mode configuration
DEMO_MODE = True
ALLOWED_TARGETS = ["localhost", "127.0.0.1", "dvwa"]


def is_allowed_target(url: str) -> bool:
    """Check if target URL is allowed in demo mode"""
    if not DEMO_MODE:
        return True
    
    parsed = urlparse(url)
    hostname = parsed.hostname or parsed.netloc
    
    # Allow localhost and DVWA container
    return any(allowed in hostname.lower() for allowed in ALLOWED_TARGETS)


async def run_scan(scan_id: str, target_url: str):
    """Run all security checks asynchronously"""
    try:
        scans[scan_id].status = "running"
        scans[scan_id].started_at = datetime.utcnow()
        
        findings: List[Finding] = []
        
        # 1. Security Headers Check
        logger.info(f"[{scan_id}] Checking security headers...")
        scans[scan_id].current_check = "Security Headers"
        scans[scan_id].progress = 10
        header_findings = await check_security_headers(target_url)
        findings.extend(header_findings)
        await asyncio.sleep(0.5)  # Simulate realistic scan timing
        
        # 2. SSL/TLS Check
        logger.info(f"[{scan_id}] Checking SSL/TLS...")
        scans[scan_id].current_check = "SSL/TLS Configuration"
        scans[scan_id].progress = 30
        ssl_findings = await check_ssl_tls(target_url)
        findings.extend(ssl_findings)
        await asyncio.sleep(0.5)
        
        # 3. XSS Detection
        logger.info(f"[{scan_id}] Checking for XSS vulnerabilities...")
        scans[scan_id].current_check = "XSS Detection"
        scans[scan_id].progress = 50
        xss_findings = await check_xss(target_url)
        findings.extend(xss_findings)
        await asyncio.sleep(0.5)
        
        # 4. SQL Injection
        logger.info(f"[{scan_id}] Checking for SQL injection...")
        scans[scan_id].current_check = "SQL Injection Detection"
        scans[scan_id].progress = 70
        sqli_findings = await check_sql_injection(target_url)
        findings.extend(sqli_findings)
        await asyncio.sleep(0.5)
        
        # 5. Information Disclosure
        logger.info(f"[{scan_id}] Checking for information disclosure...")
        scans[scan_id].current_check = "Information Disclosure"
        scans[scan_id].progress = 90
        info_findings = await check_info_disclosure(target_url)
        findings.extend(info_findings)
        
        # Complete scan
        scans[scan_id].findings = findings
        scans[scan_id].status = "completed"
        scans[scan_id].progress = 100
        scans[scan_id].completed_at = datetime.utcnow()
        scans[scan_id].current_check = "Completed"
        
        # Calculate statistics
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for finding in findings:
            severity_counts[finding.severity] += 1
        scans[scan_id].summary = severity_counts
        
        logger.info(f"[{scan_id}] Scan completed with {len(findings)} findings")
        
    except Exception as e:
        logger.error(f"[{scan_id}] Scan failed: {str(e)}")
        scans[scan_id].status = "failed"
        scans[scan_id].error = str(e)


@app.post("/api/scan", response_model=Dict)
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """Start a new vulnerability scan"""
    
    # Validate target URL in demo mode
    if not is_allowed_target(request.target_url):
        raise HTTPException(
            status_code=403,
            detail="Demo mode: Only localhost and DVWA targets are allowed. "
                   "Deploy your own instance to scan external targets."
        )
    
    # Generate scan ID
    scan_id = str(uuid.uuid4())
    
    # Initialize scan result
    scan_result = ScanResult(
        scan_id=scan_id,
        target_url=request.target_url,
        status="queued",
        progress=0,
        findings=[],
        created_at=datetime.utcnow()
    )
    
    scans[scan_id] = scan_result
    
    # Start scan in background
    background_tasks.add_task(run_scan, scan_id, request.target_url)
    
    return {
        "scan_id": scan_id,
        "status": "queued",
        "message": "Scan started successfully"
    }


@app.get("/api/scan/{scan_id}", response_model=ScanResult)
async def get_scan_status(scan_id: str):
    """Get scan status and results"""
    if scan_id not in scans:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return scans[scan_id]


@app.get("/api/scan/{scan_id}/report")
async def download_report(scan_id: str):
    """Download scan report as JSON"""
    if scan_id not in scans:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scan = scans[scan_id]
    
    if scan.status != "completed":
        raise HTTPException(status_code=400, detail="Scan not completed yet")
    
    # Generate report
    report = {
        "scan_id": scan.scan_id,
        "target_url": scan.target_url,
        "scan_date": scan.created_at.isoformat(),
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        "summary": scan.summary,
        "findings": [
            {
                "title": f.title,
                "severity": f.severity,
                "description": f.description,
                "evidence": f.evidence,
                "remediation": f.remediation,
                "cwe_id": f.cwe_id,
                "owasp_category": f.owasp_category
            }
            for f in scan.findings
        ]
    }
    
    return JSONResponse(content=report)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "demo_mode": DEMO_MODE,
        "allowed_targets": ALLOWED_TARGETS if DEMO_MODE else "all"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
