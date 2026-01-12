import aiohttp
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from models import Finding


# SQL injection payloads designed to trigger errors
SQL_PAYLOADS = [
    "'",
    "1' OR '1'='1",
    "' OR '1'='1' --",
    "admin'--",
    "1' AND 1=1--",
    "' UNION SELECT NULL--",
]

# Common SQL error signatures
SQL_ERRORS = [
    "mysql",
    "sql syntax",
    "sqlite",
    "postgresql",
    "oracle",
    "odbc",
    "microsoft sql",
    "syntax error",
    "unclosed quotation",
    "quoted string not properly terminated",
]


async def check_sql_injection(target_url: str) -> List[Finding]:
    """Check for SQL injection vulnerabilities"""
    findings = []
    
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Get the page to find forms and parameters
            async with session.get(target_url, ssl=False) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Check URL parameters
                parsed = urlparse(target_url)
                params = parse_qs(parsed.query)
                
                if params:
                    for param_name in params.keys():
                        for payload in SQL_PAYLOADS[:3]:  # Test first 3 payloads
                            test_params = params.copy()
                            test_params[param_name] = [payload]
                            
                            test_url = urlunparse((
                                parsed.scheme,
                                parsed.netloc,
                                parsed.path,
                                parsed.params,
                                urlencode(test_params, doseq=True),
                                parsed.fragment
                            ))
                            
                            try:
                                async with session.get(test_url, ssl=False) as test_response:
                                    test_html = await test_response.text()
                                    test_html_lower = test_html.lower()
                                    
                                    # Check for SQL errors
                                    for error_sig in SQL_ERRORS:
                                        if error_sig in test_html_lower:
                                            findings.append(Finding(
                                                title="SQL Injection Vulnerability (Error-Based)",
                                                severity="critical",
                                                description=f"Parameter '{param_name}' appears vulnerable to SQL injection. SQL error messages were triggered.",
                                                evidence=f"Payload '{payload}' triggered SQL error pattern: '{error_sig}'",
                                                remediation="Use parameterized queries (prepared statements) for all database operations. Never concatenate user input into SQL queries. Implement input validation and least privilege database access.",
                                                cwe_id="CWE-89",
                                                owasp_category="A03:2021 - Injection"
                                            ))
                                            return findings  # Return after first finding
                            except Exception:
                                pass
                
                # Check forms for SQL injection
                forms = soup.find_all('form')
                
                for i, form in enumerate(forms[:3]):  # Limit to first 3 forms
                    form_action = form.get('action', '')
                    form_method = form.get('method', 'get').lower()
                    
                    if form_action:
                        form_url = urljoin(target_url, form_action)
                    else:
                        form_url = target_url
                    
                    # Find input fields
                    inputs = form.find_all(['input', 'textarea'])
                    
                    for input_field in inputs:
                        input_name = input_field.get('name')
                        input_type = input_field.get('type', 'text')
                        
                        if input_name and input_type not in ['submit', 'button', 'image', 'reset']:
                            # Build form data with SQL payload
                            form_data = {}
                            for inp in inputs:
                                inp_name = inp.get('name')
                                if inp_name:
                                    if inp_name == input_name:
                                        form_data[inp_name] = SQL_PAYLOADS[0]
                                    else:
                                        form_data[inp_name] = 'test'
                            
                            try:
                                if form_method == 'post':
                                    async with session.post(form_url, data=form_data, ssl=False) as test_response:
                                        test_html = await test_response.text()
                                        test_html_lower = test_html.lower()
                                        
                                        for error_sig in SQL_ERRORS:
                                            if error_sig in test_html_lower:
                                                findings.append(Finding(
                                                    title=f"SQL Injection in Form #{i+1}",
                                                    severity="critical",
                                                    description=f"Form field '{input_name}' appears vulnerable to SQL injection.",
                                                    evidence=f"SQL error pattern detected: '{error_sig}'",
                                                    remediation="Use parameterized queries (prepared statements). Never concatenate user input into SQL queries.",
                                                    cwe_id="CWE-89",
                                                    owasp_category="A03:2021 - Injection"
                                                ))
                                                return findings  # Return after first finding
                                else:
                                    async with session.get(form_url, params=form_data, ssl=False) as test_response:
                                        test_html = await test_response.text()
                                        test_html_lower = test_html.lower()
                                        
                                        for error_sig in SQL_ERRORS:
                                            if error_sig in test_html_lower:
                                                findings.append(Finding(
                                                    title=f"SQL Injection in Form #{i+1}",
                                                    severity="critical",
                                                    description=f"Form field '{input_name}' appears vulnerable to SQL injection.",
                                                    evidence=f"SQL error pattern detected: '{error_sig}'",
                                                    remediation="Use parameterized queries (prepared statements). Never concatenate user input into SQL queries.",
                                                    cwe_id="CWE-89",
                                                    owasp_category="A03:2021 - Injection"
                                                ))
                                                return findings  # Return after first finding
                            except Exception:
                                pass
                
                # If no SQL injection found
                if not findings:
                    findings.append(Finding(
                        title="No SQL Injection Detected",
                        severity="info",
                        description="No obvious SQL injection vulnerabilities were detected in basic testing.",
                        evidence="Error-based SQL injection payloads did not trigger database errors",
                        remediation="This does not guarantee absence of SQL injection. Perform comprehensive testing with advanced techniques.",
                        cwe_id=None,
                        owasp_category=None
                    ))
    
    except aiohttp.ClientError as e:
        findings.append(Finding(
            title="SQL Injection Check Error",
            severity="info",
            description="Unable to perform SQL injection checks.",
            evidence=f"Error: {str(e)}",
            remediation="Verify target accessibility.",
            cwe_id=None,
            owasp_category=None
        ))
    
    except Exception as e:
        findings.append(Finding(
            title="SQL Injection Check Error",
            severity="info",
            description="An error occurred during SQL injection analysis.",
            evidence=f"Error: {str(e)}",
            remediation="Review error and try again.",
            cwe_id=None,
            owasp_category=None
        ))
    
    return findings
