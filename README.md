# VulnScan - Web Vulnerability Scanner

A professional-grade web vulnerability scanner built for security portfolios and educational purposes. Features automated detection of common web vulnerabilities including XSS, SQL injection, security header issues, and SSL/TLS misconfigurations.

![VulnScan](https://img.shields.io/badge/Security-Scanner-cyan)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![React](https://img.shields.io/badge/React-18-61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688)

## 🔒 Features

### Security Checks
- **Security Headers Analysis**: HSTS, CSP, X-Frame-Options, X-Content-Type-Options, and more
- **SSL/TLS Configuration**: Certificate validation, protocol versions, cipher strength
- **XSS Detection**: Reflected XSS testing on forms and URL parameters
- **SQL Injection**: Error-based SQL injection detection
- **Information Disclosure**: Sensitive file exposure, directory listing, error messages

### Technical Features
- Real-time scan progress tracking
- Professional, security-focused dark theme UI
- Exportable JSON reports
- CWE and OWASP categorization
- Severity-based finding classification (Critical, High, Medium, Low, Info)
- Demo mode with localhost-only scanning for safe portfolio demonstrations

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Ports 3000, 8000, and 8080 available

### Installation

1. **Clone or extract the project**
```bash
cd vulnscan
```

2. **Start all services**
```bash
docker-compose up --build
```

This single command will:
- Build and start the FastAPI backend (port 8000)
- Build and start the React frontend (port 3000)
- Pull and start DVWA test target (port 8080)

3. **Access the application**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- DVWA Test Target: http://localhost:8080

### First Scan

1. Navigate to http://localhost:3000
2. Click on "DVWA (localhost:8080)" demo target
3. Click "Start Security Scan"
4. Watch the real-time progress
5. Review findings and download the JSON report

## 📁 Project Structure

```
vulnscan/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── scanners/
│   │   ├── headers.py       # Security headers check
│   │   ├── ssl_check.py     # SSL/TLS analysis
│   │   ├── xss.py           # XSS detection
│   │   ├── sqli.py          # SQL injection detection
│   │   └── info_disclosure.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ScanForm.jsx
│   │   │   ├── ScanProgress.jsx
│   │   │   ├── ReportView.jsx
│   │   │   └── FindingCard.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 API Documentation

### Endpoints

#### `POST /api/scan`
Start a new security scan.

**Request:**
```json
{
  "target_url": "http://localhost:8080"
}
```

**Response:**
```json
{
  "scan_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued",
  "message": "Scan started successfully"
}
```

#### `GET /api/scan/{scan_id}`
Get scan status and results.

**Response:**
```json
{
  "scan_id": "123e4567-e89b-12d3-a456-426614174000",
  "target_url": "http://localhost:8080",
  "status": "completed",
  "progress": 100,
  "findings": [...],
  "summary": {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 5,
    "info": 4
  }
}
```

#### `GET /api/scan/{scan_id}/report`
Download full JSON report.

#### `GET /api/health`
Health check endpoint.

## 🎯 Demo Mode

By default, VulnScan runs in **demo mode** for portfolio demonstrations:

- ✅ Only allows scanning localhost and DVWA container
- ✅ Safe for public demos
- ✅ Prevents abuse of the scanner

To disable demo mode for production use:
1. Edit `backend/main.py`
2. Set `DEMO_MODE = False`
3. Rebuild: `docker-compose up --build`

## 🛡️ Security Considerations

### For Portfolio Use
- Demo mode restricts scanning to localhost only
- No persistent storage of scan results
- Ideal for demonstrations and education

### For Production Use
- Implement authentication and authorization
- Add rate limiting
- Use database for scan persistence
- Enable HTTPS
- Add IP whitelisting
- Implement comprehensive logging

## 🧪 Testing with DVWA

The included DVWA (Damn Vulnerable Web Application) container provides a perfect testing environment:

1. Access DVWA at http://localhost:8080
2. Default credentials: `admin` / `password`
3. Set security level to "Low" for maximum findings
4. Run a scan and observe detected vulnerabilities

**Expected Findings:**
- Missing security headers (HSTS, CSP, etc.)
- No SSL/TLS (HTTP only)
- Potential XSS vulnerabilities
- SQL injection opportunities
- Information disclosure

## 🔨 Development

### Running Backend Locally
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Running Frontend Locally
```bash
cd frontend
npm install
npm run dev
```

### Tech Stack
- **Backend**: Python 3.12, FastAPI, aiohttp, BeautifulSoup4
- **Frontend**: React 18, Vite, TailwindCSS
- **Deployment**: Docker, Docker Compose

## 📊 Report Format

Findings include:
- **Title**: Clear description of the issue
- **Severity**: Critical, High, Medium, Low, Info
- **Description**: Detailed explanation
- **Evidence**: Specific proof of the vulnerability
- **Remediation**: Step-by-step fix instructions
- **CWE ID**: Common Weakness Enumeration reference
- **OWASP Category**: OWASP Top 10 classification

## 🚧 Limitations

This is a portfolio/educational project with intentional limitations:

- Basic detection patterns (not comprehensive like commercial tools)
- Error-based SQL injection only (no blind SQLi)
- Reflected XSS only (no stored or DOM-based)
- Limited crawling (form and parameter discovery)
- No authenticated scanning
- Synchronous scanning (one at a time)

For production security testing, use professional tools like:
- OWASP ZAP
- Burp Suite
- Acunetix
- Nessus

## 📝 License

This project is for educational and portfolio purposes. Use responsibly and only scan targets you own or have permission to test.

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome! Feel free to:
- Report bugs
- Suggest improvements
- Share your scan results

## 📧 Contact

Built as a security portfolio project demonstrating:
- Web security vulnerability detection
- FastAPI backend development
- Modern React frontend with TailwindCSS
- Docker containerization
- Security best practices

---

**⚠️ Disclaimer**: Only use this tool on systems you own or have explicit permission to test. Unauthorized security testing is illegal.
