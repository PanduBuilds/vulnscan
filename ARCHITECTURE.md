# VulnScan Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│                     (http://localhost:3000)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP Requests
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    React Frontend                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Components:                                          │  │
│  │  • ScanForm.jsx      - URL input & demo targets      │  │
│  │  • ScanProgress.jsx  - Real-time progress tracking   │  │
│  │  • ReportView.jsx    - Results & filtering           │  │
│  │  • FindingCard.jsx   - Individual vulnerabilities    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Technologies: React 18, Vite, TailwindCSS                  │
│  Port: 3000                                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ REST API Calls
                         │ (GET, POST)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Endpoints:                                           │  │
│  │  • POST   /api/scan           - Start scan           │  │
│  │  • GET    /api/scan/{id}      - Get status           │  │
│  │  • GET    /api/scan/{id}/report - Download report    │  │
│  │  • GET    /api/health         - Health check         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Security Scanners:                                   │  │
│  │  1. headers.py        - Security headers analysis    │  │
│  │  2. ssl_check.py      - SSL/TLS validation           │  │
│  │  3. xss.py            - XSS detection                │  │
│  │  4. sqli.py           - SQL injection testing        │  │
│  │  5. info_disclosure.py - Information leaks           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Technologies: Python 3.12, FastAPI, aiohttp, BeautifulSoup│
│  Port: 8000                                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP Requests
                         │ (Security Checks)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Target Application                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  DVWA (Damn Vulnerable Web Application)              │  │
│  │  • Intentionally vulnerable for testing              │  │
│  │  • Multiple security flaws                           │  │
│  │  • Perfect for scanner demonstrations                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Port: 8080                                                  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Starting a Scan

```
User Action (Frontend)
    │
    ├─► Enter target URL
    │
    ├─► Click "Start Security Scan"
    │
    └─► POST /api/scan
         │
         ├─► FastAPI receives request
         │
         ├─► Validates URL (demo mode check)
         │
         ├─► Generates unique scan_id
         │
         ├─► Stores scan in memory
         │
         ├─► Starts background task
         │
         └─► Returns scan_id to frontend
              │
              └─► Frontend navigates to progress view
```

### 2. Scan Execution (Backend)

```
Background Task Starts
    │
    ├─► Update status: "running"
    │
    ├─► Progress: 10% - Security Headers Check
    │    │
    │    ├─► HTTP GET to target
    │    ├─► Analyze response headers
    │    ├─► Check for HSTS, CSP, X-Frame-Options, etc.
    │    └─► Generate findings
    │
    ├─► Progress: 30% - SSL/TLS Analysis
    │    │
    │    ├─► Parse URL scheme
    │    ├─► If HTTPS: establish SSL connection
    │    ├─► Check certificate validity
    │    ├─► Verify protocol version
    │    └─► Generate findings
    │
    ├─► Progress: 50% - XSS Detection
    │    │
    │    ├─► HTTP GET to target
    │    ├─► Parse HTML for forms
    │    ├─► Test parameters with XSS payloads
    │    ├─► Check for reflection
    │    └─► Generate findings
    │
    ├─► Progress: 70% - SQL Injection Detection
    │    │
    │    ├─► Parse forms and parameters
    │    ├─► Submit SQL injection payloads
    │    ├─► Analyze responses for error patterns
    │    └─► Generate findings
    │
    ├─► Progress: 90% - Information Disclosure
    │    │
    │    ├─► Check for sensitive files (.git, .env)
    │    ├─► Analyze HTML comments
    │    ├─► Check for directory listings
    │    ├─► Look for error messages
    │    └─► Generate findings
    │
    └─► Progress: 100% - Complete
         │
         ├─► Update status: "completed"
         ├─► Calculate summary statistics
         └─► Store final results
```

### 3. Progress Tracking (Frontend)

```
Progress View Mounted
    │
    ├─► Start polling (every 1 second)
    │
    └─► GET /api/scan/{scan_id}
         │
         ├─► Receive current status
         │    │
         │    ├─► progress: 0-100
         │    ├─► current_check: string
         │    ├─► findings: array
         │    └─► status: queued|running|completed|failed
         │
         ├─► Update UI
         │    │
         │    ├─► Progress bar
         │    ├─► Current check label
         │    └─► Check list (✓ completed)
         │
         └─► If status === "completed"
              │
              ├─► Stop polling
              ├─► Wait 1 second (smooth transition)
              └─► Navigate to report view
```

### 4. Report Display

```
Report View Mounted
    │
    ├─► Receive scan data
    │
    ├─► Calculate statistics
    │    │
    │    ├─► Count by severity
    │    ├─► Total findings
    │    └─► Critical count
    │
    ├─► Render summary cards
    │
    ├─► Display findings list
    │    │
    │    └─► For each finding:
    │         │
    │         ├─► Severity badge
    │         ├─► Title
    │         ├─► CWE/OWASP tags
    │         └─► Expandable details
    │              │
    │              ├─► Description
    │              ├─► Evidence
    │              └─► Remediation
    │
    └─► Enable actions
         │
         ├─► Filter by severity
         ├─► Download JSON report
         └─► Start new scan
```

## Component Interaction

### Frontend Components

```
App.jsx (Root)
    │
    ├─► State Management
    │    ├─► currentView: 'form' | 'progress' | 'report'
    │    ├─► scanId: string
    │    └─► scanData: object
    │
    └─► Conditional Rendering
         │
         ├─► if currentView === 'form'
         │    └─► <ScanForm onScanStart={handleScanStart} />
         │
         ├─► if currentView === 'progress'
         │    └─► <ScanProgress 
         │             scanId={scanId}
         │             onComplete={handleScanComplete}
         │         />
         │
         └─► if currentView === 'report'
              └─► <ReportView 
                       scanData={scanData}
                       onNewScan={handleNewScan}
                   />
                   │
                   └─► <FindingCard finding={...} /> (multiple)
```

### Backend Modules

```
main.py (FastAPI App)
    │
    ├─► Route Handlers
    │    ├─► /api/scan (POST)
    │    ├─► /api/scan/{id} (GET)
    │    ├─► /api/scan/{id}/report (GET)
    │    └─► /api/health (GET)
    │
    ├─► Background Tasks
    │    └─► run_scan(scan_id, target_url)
    │         │
    │         └─► Orchestrates all scanners
    │
    └─► In-Memory Storage
         └─► scans: Dict[str, ScanResult]

models.py (Data Schemas)
    │
    ├─► ScanRequest
    ├─► ScanResult
    └─► Finding

scanners/ (Detection Logic)
    │
    ├─► headers.py
    │    └─► async check_security_headers() -> List[Finding]
    │
    ├─► ssl_check.py
    │    └─► async check_ssl_tls() -> List[Finding]
    │
    ├─► xss.py
    │    └─► async check_xss() -> List[Finding]
    │
    ├─► sqli.py
    │    └─► async check_sql_injection() -> List[Finding]
    │
    └─► info_disclosure.py
         └─► async check_info_disclosure() -> List[Finding]
```

## Security Considerations

### Demo Mode Protection

```python
# In main.py

DEMO_MODE = True
ALLOWED_TARGETS = ["localhost", "127.0.0.1", "dvwa"]

def is_allowed_target(url: str) -> bool:
    if not DEMO_MODE:
        return True
    
    parsed = urlparse(url)
    hostname = parsed.hostname or parsed.netloc
    
    return any(allowed in hostname.lower() 
               for allowed in ALLOWED_TARGETS)
```

This prevents:
- Scanning external websites
- Potential abuse of the scanner
- Legal issues from unauthorized testing
- Resource exhaustion

### Input Validation

```python
# Pydantic model validation
class ScanRequest(BaseModel):
    target_url: str  # Must be a string
    
    # FastAPI automatically validates:
    # - Required field (...)
    # - Type checking
    # - JSON parsing
```

### Error Handling

Each scanner wraps its logic in try/except to prevent crashes:

```python
try:
    # Scanner logic
    findings = perform_checks(target)
except aiohttp.ClientError as e:
    # Network errors
    findings.append(error_finding)
except Exception as e:
    # Unexpected errors
    findings.append(generic_error_finding)
```

## Deployment Architecture

### Docker Compose Network

```
┌─────────────────────────────────────────────┐
│         Docker Network: vulnscan-network    │
│                                             │
│  ┌──────────────┐  ┌──────────────┐        │
│  │   frontend   │  │   backend    │        │
│  │   :3000      │◄─┤   :8000      │        │
│  └──────┬───────┘  └──────┬───────┘        │
│         │                  │                │
│         │                  │                │
│         │         ┌────────▼──────┐         │
│         │         │     dvwa      │         │
│         │         │     :80       │         │
│         │         └───────────────┘         │
│         │                                   │
└─────────┼───────────────────────────────────┘
          │
          │ Port Mapping
          │
    ┌─────▼──────┐
    │    Host    │
    │  :3000     │ Frontend
    │  :8000     │ Backend API
    │  :8080     │ DVWA
    └────────────┘
```

## Performance Characteristics

### Request Flow Timing

```
Total Scan Time: ~10-20 seconds
│
├─► API Request/Response: ~50ms
│
├─► Security Headers: ~2-3s
│    ├─► HTTP GET: 500ms
│    └─► Analysis: 100ms
│
├─► SSL/TLS Check: ~2-3s
│    ├─► Connection: 1s
│    └─► Certificate parsing: 100ms
│
├─► XSS Detection: ~3-5s
│    ├─► Page fetch: 500ms
│    ├─► Form discovery: 200ms
│    └─► Payload testing: 2-3s
│
├─► SQL Injection: ~3-5s
│    ├─► Form discovery: 200ms
│    └─► Payload testing: 2-3s
│
└─► Information Disclosure: ~2-3s
     ├─► File checks: 1-2s
     └─► Content analysis: 500ms
```

### Resource Usage

```
Container Memory Usage:
├─► Backend:  ~100MB
├─► Frontend: ~50MB
└─► DVWA:     ~150MB
Total:        ~300MB

CPU Usage (during scan):
├─► Backend:  10-20%
├─► Frontend: 5-10%
└─► DVWA:     5-10%
```

## Scalability Considerations

### Current Limitations

1. **Single Scan at a Time**: No task queue
2. **In-Memory Storage**: Lost on restart
3. **No Authentication**: Public access
4. **Synchronous Execution**: Sequential checks

### Scaling Solutions

```
Production Architecture:

┌─────────┐
│  Nginx  │ Load Balancer
│  (SSL)  │
└────┬────┘
     │
     ├─► Frontend Instances (3x)
     │   └─► Served from CDN
     │
     └─► Backend Instances (5x)
          │
          ├─► Redis (Session & Cache)
          │
          ├─► PostgreSQL (Scan History)
          │
          └─► Celery Workers (10x)
               └─► Parallel Scans
```

---

This architecture provides a solid foundation for a portfolio-quality vulnerability scanner while remaining simple enough to understand and modify.
