import ssl
import socket
import aiohttp
from typing import List
from datetime import datetime
from urllib.parse import urlparse
from models import Finding


async def check_ssl_tls(target_url: str) -> List[Finding]:
    """Check SSL/TLS configuration and certificate"""
    findings = []
    
    parsed = urlparse(target_url)
    
    # Only check HTTPS URLs
    if parsed.scheme != "https":
        findings.append(Finding(
            title="HTTP Only - No SSL/TLS",
            severity="high",
            description="The application is served over HTTP without encryption. All traffic is transmitted in clear text.",
            evidence=f"URL scheme: {parsed.scheme}",
            remediation="Implement HTTPS with a valid SSL/TLS certificate. Redirect all HTTP traffic to HTTPS.",
            cwe_id="CWE-319",
            owasp_category="A02:2021 - Cryptographic Failures"
        ))
        return findings
    
    hostname = parsed.hostname
    port = parsed.port or 443
    
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Try to connect and get certificate
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                
                # Check certificate expiration
                if cert:
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    if days_until_expiry < 0:
                        findings.append(Finding(
                            title="Expired SSL Certificate",
                            severity="critical",
                            description="The SSL certificate has expired.",
                            evidence=f"Certificate expired on: {cert['notAfter']}",
                            remediation="Renew the SSL certificate immediately.",
                            cwe_id="CWE-295",
                            owasp_category="A02:2021 - Cryptographic Failures"
                        ))
                    elif days_until_expiry < 30:
                        findings.append(Finding(
                            title="SSL Certificate Expiring Soon",
                            severity="medium",
                            description=f"The SSL certificate will expire in {days_until_expiry} days.",
                            evidence=f"Certificate expires on: {cert['notAfter']}",
                            remediation="Renew the SSL certificate before expiration.",
                            cwe_id="CWE-295",
                            owasp_category="A02:2021 - Cryptographic Failures"
                        ))
                
                # Check SSL/TLS protocol version
                protocol_version = ssock.version()
                if protocol_version in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
                    findings.append(Finding(
                        title="Weak SSL/TLS Protocol Version",
                        severity="high",
                        description=f"The server supports weak protocol version: {protocol_version}",
                        evidence=f"Negotiated protocol: {protocol_version}",
                        remediation="Disable SSLv2, SSLv3, TLSv1.0, and TLSv1.1. Use TLSv1.2 or TLSv1.3.",
                        cwe_id="CWE-327",
                        owasp_category="A02:2021 - Cryptographic Failures"
                    ))
                else:
                    findings.append(Finding(
                        title="Strong SSL/TLS Protocol",
                        severity="info",
                        description=f"The server uses a secure protocol version: {protocol_version}",
                        evidence=f"Negotiated protocol: {protocol_version}",
                        remediation="Continue using secure TLS versions.",
                        cwe_id=None,
                        owasp_category=None
                    ))
                
                # Check cipher suite
                cipher = ssock.cipher()
                if cipher:
                    cipher_name = cipher[0]
                    # Check for weak ciphers
                    weak_indicators = ["RC4", "DES", "MD5", "NULL", "EXPORT", "anon"]
                    if any(indicator in cipher_name.upper() for indicator in weak_indicators):
                        findings.append(Finding(
                            title="Weak Cipher Suite",
                            severity="high",
                            description=f"The server negotiated a weak cipher suite.",
                            evidence=f"Cipher: {cipher_name}",
                            remediation="Disable weak cipher suites. Use strong ciphers like AES-GCM.",
                            cwe_id="CWE-327",
                            owasp_category="A02:2021 - Cryptographic Failures"
                        ))
    
    except ssl.SSLError as e:
        findings.append(Finding(
            title="SSL/TLS Configuration Error",
            severity="medium",
            description="SSL/TLS handshake failed.",
            evidence=f"SSL Error: {str(e)}",
            remediation="Review SSL/TLS configuration and ensure valid certificates are installed.",
            cwe_id="CWE-295",
            owasp_category="A02:2021 - Cryptographic Failures"
        ))
    
    except socket.timeout:
        findings.append(Finding(
            title="Connection Timeout",
            severity="info",
            description="Connection to the server timed out during SSL/TLS check.",
            evidence="Socket timeout after 10 seconds",
            remediation="Verify server is accessible and responding.",
            cwe_id=None,
            owasp_category=None
        ))
    
    except Exception as e:
        findings.append(Finding(
            title="SSL/TLS Check Error",
            severity="info",
            description="An error occurred during SSL/TLS analysis.",
            evidence=f"Error: {str(e)}",
            remediation="Review the error and configuration.",
            cwe_id=None,
            owasp_category=None
        ))
    
    return findings
