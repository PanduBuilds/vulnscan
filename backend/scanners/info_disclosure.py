import aiohttp
from bs4 import BeautifulSoup
from typing import List
from models import Finding


async def check_info_disclosure(target_url: str) -> List[Finding]:
    """Check for information disclosure vulnerabilities"""
    findings = []
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(target_url, ssl=False) as response:
                html = await response.text()
                headers = response.headers
                
                # Check for common development/debug files
                debug_files = [
                    '.git/config',
                    '.env',
                    'phpinfo.php',
                    'info.php',
                    '.DS_Store',
                    'web.config',
                    '.htaccess',
                    'composer.json',
                    'package.json',
                ]
                
                for debug_file in debug_files:
                    try:
                        test_url = target_url.rstrip('/') + '/' + debug_file
                        async with session.get(test_url, ssl=False) as test_response:
                            if test_response.status == 200:
                                findings.append(Finding(
                                    title=f"Sensitive File Accessible: {debug_file}",
                                    severity="high",
                                    description=f"The file '{debug_file}' is publicly accessible.",
                                    evidence=f"HTTP {test_response.status} response for {test_url}",
                                    remediation=f"Remove or restrict access to '{debug_file}'. Configure web server to deny access to sensitive files.",
                                    cwe_id="CWE-200",
                                    owasp_category="A01:2021 - Broken Access Control"
                                ))
                    except Exception:
                        pass  # File not accessible or error
                
                # Check for directory listing
                soup = BeautifulSoup(html, 'html.parser')
                page_text = soup.get_text().lower()
                
                directory_indicators = ['index of /', 'parent directory', 'directory listing']
                if any(indicator in page_text for indicator in directory_indicators):
                    findings.append(Finding(
                        title="Directory Listing Enabled",
                        severity="medium",
                        description="Directory listing appears to be enabled, potentially exposing file structure.",
                        evidence="Page contains directory listing indicators",
                        remediation="Disable directory listing in web server configuration.",
                        cwe_id="CWE-548",
                        owasp_category="A05:2021 - Security Misconfiguration"
                    ))
                
                # Check for HTML comments with sensitive info
                comments = soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in str(text))
                sensitive_keywords = ['password', 'secret', 'key', 'token', 'api', 'todo', 'fixme', 'hack']
                
                for comment in comments:
                    comment_lower = str(comment).lower()
                    if any(keyword in comment_lower for keyword in sensitive_keywords):
                        findings.append(Finding(
                            title="Sensitive Information in HTML Comments",
                            severity="medium",
                            description="HTML comments may contain sensitive information.",
                            evidence=f"Comment contains keywords: {', '.join([k for k in sensitive_keywords if k in comment_lower])}",
                            remediation="Remove sensitive comments from production code. Implement a build process that strips comments.",
                            cwe_id="CWE-615",
                            owasp_category="A05:2021 - Security Misconfiguration"
                        ))
                        break  # Only report once
                
                # Check for error messages revealing stack traces
                error_indicators = [
                    'stack trace',
                    'exception',
                    'error in',
                    'line number',
                    'fatal error',
                    'warning:',
                    'parse error',
                ]
                
                for indicator in error_indicators:
                    if indicator in page_text:
                        findings.append(Finding(
                            title="Detailed Error Messages Exposed",
                            severity="medium",
                            description="The application exposes detailed error messages that may reveal internal structure.",
                            evidence=f"Error indicator found: '{indicator}'",
                            remediation="Configure application to display generic error messages to users. Log detailed errors server-side only.",
                            cwe_id="CWE-209",
                            owasp_category="A05:2021 - Security Misconfiguration"
                        ))
                        break  # Only report once
                
                # Check for version numbers in content
                import re
                version_pattern = r'v?\d+\.\d+\.\d+'
                version_matches = re.findall(version_pattern, html)
                
                if len(version_matches) > 3:  # Multiple version numbers might indicate version disclosure
                    findings.append(Finding(
                        title="Potential Version Information Disclosure",
                        severity="low",
                        description="Multiple version numbers detected in page content.",
                        evidence=f"Found {len(version_matches)} version number patterns",
                        remediation="Avoid exposing version numbers of frameworks, libraries, or server software.",
                        cwe_id="CWE-200",
                        owasp_category="A05:2021 - Security Misconfiguration"
                    ))
                
                # Check robots.txt for sensitive paths
                try:
                    robots_url = target_url.rstrip('/').split('/', 3)[0:3]
                    robots_url = '/'.join(robots_url) + '/robots.txt'
                    
                    async with session.get(robots_url, ssl=False) as robots_response:
                        if robots_response.status == 200:
                            robots_text = await robots_response.text()
                            
                            sensitive_paths = ['admin', 'backup', 'private', 'config', '.git']
                            found_sensitive = [path for path in sensitive_paths if path in robots_text.lower()]
                            
                            if found_sensitive:
                                findings.append(Finding(
                                    title="Robots.txt Reveals Sensitive Paths",
                                    severity="info",
                                    description="The robots.txt file discloses potentially sensitive directories.",
                                    evidence=f"Sensitive paths in robots.txt: {', '.join(found_sensitive)}",
                                    remediation="While robots.txt is useful for SEO, avoid listing truly sensitive paths. Use proper access controls instead.",
                                    cwe_id="CWE-200",
                                    owasp_category="A01:2021 - Broken Access Control"
                                ))
                except Exception:
                    pass  # robots.txt not found or inaccessible
    
    except aiohttp.ClientError as e:
        findings.append(Finding(
            title="Information Disclosure Check Error",
            severity="info",
            description="Unable to perform information disclosure checks.",
            evidence=f"Error: {str(e)}",
            remediation="Verify target accessibility.",
            cwe_id=None,
            owasp_category=None
        ))
    
    except Exception as e:
        findings.append(Finding(
            title="Information Disclosure Check Error",
            severity="info",
            description="An error occurred during information disclosure analysis.",
            evidence=f"Error: {str(e)}",
            remediation="Review error and try again.",
            cwe_id=None,
            owasp_category=None
        ))
    
    return findings
