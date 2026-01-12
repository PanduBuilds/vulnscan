import aiohttp
from typing import List
from models import Finding


SECURITY_HEADERS = {
    "Strict-Transport-Security": {
        "severity": "medium",
        "description": "HTTP Strict Transport Security (HSTS) ensures the browser only connects via HTTPS.",
        "remediation": "Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload' header to all HTTPS responses.",
        "cwe_id": "CWE-523",
        "owasp": "A05:2021 - Security Misconfiguration"
    },
    "Content-Security-Policy": {
        "severity": "high",
        "description": "Content Security Policy (CSP) helps prevent XSS attacks by controlling which resources can be loaded.",
        "remediation": "Implement a Content-Security-Policy header with appropriate directives for your application.",
        "cwe_id": "CWE-1021",
        "owasp": "A03:2021 - Injection"
    },
    "X-Frame-Options": {
        "severity": "medium",
        "description": "X-Frame-Options prevents clickjacking attacks by controlling whether the page can be embedded in frames.",
        "remediation": "Add 'X-Frame-Options: DENY' or 'X-Frame-Options: SAMEORIGIN' header.",
        "cwe_id": "CWE-1021",
        "owasp": "A05:2021 - Security Misconfiguration"
    },
    "X-Content-Type-Options": {
        "severity": "low",
        "description": "X-Content-Type-Options prevents MIME-sniffing attacks.",
        "remediation": "Add 'X-Content-Type-Options: nosniff' header to all responses.",
        "cwe_id": "CWE-16",
        "owasp": "A05:2021 - Security Misconfiguration"
    },
    "X-XSS-Protection": {
        "severity": "low",
        "description": "X-XSS-Protection enables browser's XSS filter (note: deprecated in favor of CSP).",
        "remediation": "Add 'X-XSS-Protection: 1; mode=block' header. Better: use Content-Security-Policy.",
        "cwe_id": "CWE-79",
        "owasp": "A03:2021 - Injection"
    },
    "Referrer-Policy": {
        "severity": "low",
        "description": "Referrer-Policy controls how much referrer information is shared with requests.",
        "remediation": "Add 'Referrer-Policy: strict-origin-when-cross-origin' or 'no-referrer' header.",
        "cwe_id": "CWE-200",
        "owasp": "A01:2021 - Broken Access Control"
    },
    "Permissions-Policy": {
        "severity": "info",
        "description": "Permissions-Policy controls which browser features can be used.",
        "remediation": "Add 'Permissions-Policy' header to restrict unnecessary browser features.",
        "cwe_id": "CWE-250",
        "owasp": "A05:2021 - Security Misconfiguration"
    }
}


async def check_security_headers(target_url: str) -> List[Finding]:
    """Check for missing or misconfigured security headers"""
    findings = []
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(target_url, ssl=False, allow_redirects=True) as response:
                headers = response.headers
                
                # Check for missing headers
                for header_name, header_info in SECURITY_HEADERS.items():
                    if header_name not in headers:
                        findings.append(Finding(
                            title=f"Missing Security Header: {header_name}",
                            severity=header_info["severity"],
                            description=header_info["description"],
                            evidence=f"Header '{header_name}' not found in response",
                            remediation=header_info["remediation"],
                            cwe_id=header_info["cwe_id"],
                            owasp_category=header_info["owasp"]
                        ))
                    else:
                        # Header present - could add validation logic here
                        pass
                
                # Check for information disclosure in Server header
                if "Server" in headers:
                    server_header = headers["Server"]
                    if any(keyword in server_header.lower() for keyword in ["apache", "nginx", "iis", "/"]):
                        findings.append(Finding(
                            title="Server Version Disclosure in Headers",
                            severity="info",
                            description="The Server header reveals software version information.",
                            evidence=f"Server: {server_header}",
                            remediation="Configure the web server to suppress or obfuscate version information in the Server header.",
                            cwe_id="CWE-200",
                            owasp_category="A05:2021 - Security Misconfiguration"
                        ))
                
                # Check for X-Powered-By header
                if "X-Powered-By" in headers:
                    findings.append(Finding(
                        title="Technology Disclosure via X-Powered-By Header",
                        severity="info",
                        description="The X-Powered-By header reveals technology stack information.",
                        evidence=f"X-Powered-By: {headers['X-Powered-By']}",
                        remediation="Remove or suppress the X-Powered-By header from responses.",
                        cwe_id="CWE-200",
                        owasp_category="A05:2021 - Security Misconfiguration"
                    ))
    
    except aiohttp.ClientError as e:
        findings.append(Finding(
            title="Connection Error",
            severity="info",
            description="Unable to connect to target for security header analysis.",
            evidence=f"Error: {str(e)}",
            remediation="Verify the target URL is accessible and try again.",
            cwe_id=None,
            owasp_category=None
        ))
    
    except Exception as e:
        findings.append(Finding(
            title="Scan Error",
            severity="info",
            description="An unexpected error occurred during security header analysis.",
            evidence=f"Error: {str(e)}",
            remediation="Review the error and try again.",
            cwe_id=None,
            owasp_category=None
        ))
    
    return findings
