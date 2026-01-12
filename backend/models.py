from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class ScanRequest(BaseModel):
    target_url: str = Field(..., description="Target URL to scan")
    
    class Config:
        json_schema_extra = {
            "example": {
                "target_url": "http://localhost:8080"
            }
        }


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Finding(BaseModel):
    title: str
    severity: str
    description: str
    evidence: str
    remediation: str
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Missing Security Header: Strict-Transport-Security",
                "severity": "medium",
                "description": "The application does not implement HTTP Strict Transport Security (HSTS).",
                "evidence": "Header 'Strict-Transport-Security' not found in response",
                "remediation": "Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains' header",
                "cwe_id": "CWE-523",
                "owasp_category": "A05:2021 - Security Misconfiguration"
            }
        }


class ScanStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanResult(BaseModel):
    scan_id: str
    target_url: str
    status: str
    progress: int = 0
    current_check: Optional[str] = None
    findings: List[Finding] = []
    summary: Optional[Dict[str, int]] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "scan_id": "123e4567-e89b-12d3-a456-426614174000",
                "target_url": "http://localhost:8080",
                "status": "completed",
                "progress": 100,
                "findings": [],
                "summary": {
                    "critical": 1,
                    "high": 2,
                    "medium": 3,
                    "low": 5,
                    "info": 4
                },
                "created_at": "2024-01-10T10:00:00",
                "completed_at": "2024-01-10T10:02:30"
            }
        }
