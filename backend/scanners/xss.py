import aiohttp
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from models import Finding


XSS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "'\"><script>alert(1)</script>",
    "javascript:alert(1)",
    "<svg/onload=alert(1)>",
]


async def check_xss(target_url: str) -> List[Finding]:
    """Check for reflected XSS vulnerabilities"""
    findings = []
    
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # First, get the page to find forms and parameters
            async with session.get(target_url, ssl=False) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find all forms
                forms = soup.find_all('form')
                
                if not forms:
                    # Check URL parameters for reflection
                    parsed = urlparse(target_url)
                    params = parse_qs(parsed.query)
                    
                    if params:
                        # Test each parameter with XSS payload
                        for param_name in params.keys():
                            test_params = params.copy()
                            test_payload = "<script>alert('XSS')</script>"
                            test_params[param_name] = [test_payload]
                            
                            # Rebuild URL with test payload
                            test_url = urlunparse((
                                parsed.scheme,
                                parsed.netloc,
                                parsed.path,
                                parsed.params,
                                urlencode(test_params, doseq=True),
                                parsed.fragment
                            ))
                            
                            async with session.get(test_url, ssl=False) as test_response:
                                test_html = await test_response.text()
                                
                                if test_payload in test_html:
                                    findings.append(Finding(
                                        title="Reflected XSS in URL Parameter",
                                        severity="high",
                                        description=f"User input from parameter '{param_name}' is reflected in the response without proper encoding.",
                                        evidence=f"Parameter '{param_name}' reflects input: {test_payload}",
                                        remediation="Implement proper output encoding/escaping for all user input. Use Content-Security-Policy header.",
                                        cwe_id="CWE-79",
                                        owasp_category="A03:2021 - Injection"
                                    ))
                    else:
                        findings.append(Finding(
                            title="No Forms or Parameters Found",
                            severity="info",
                            description="No forms or URL parameters were found to test for XSS.",
                            evidence="Page contains no testable input vectors",
                            remediation="Manual testing may be required for XSS vulnerabilities.",
                            cwe_id=None,
                            owasp_category=None
                        ))
                else:
                    # Test forms for XSS
                    for i, form in enumerate(forms[:3]):  # Limit to first 3 forms
                        form_action = form.get('action', '')
                        form_method = form.get('method', 'get').lower()
                        
                        # Build form URL
                        if form_action:
                            form_url = urljoin(target_url, form_action)
                        else:
                            form_url = target_url
                        
                        # Find input fields
                        inputs = form.find_all(['input', 'textarea'])
                        form_data = {}
                        
                        for input_field in inputs:
                            input_name = input_field.get('name')
                            input_type = input_field.get('type', 'text')
                            
                            if input_name and input_type not in ['submit', 'button', 'hidden']:
                                form_data[input_name] = XSS_PAYLOADS[0]
                        
                        if form_data:
                            try:
                                if form_method == 'post':
                                    async with session.post(form_url, data=form_data, ssl=False) as test_response:
                                        test_html = await test_response.text()
                                        
                                        if XSS_PAYLOADS[0] in test_html:
                                            findings.append(Finding(
                                                title=f"Reflected XSS in Form #{i+1}",
                                                severity="high",
                                                description="Form input is reflected in the response without proper encoding.",
                                                evidence=f"Form at {form_url} reflects XSS payload",
                                                remediation="Implement proper output encoding/escaping for all form inputs. Use Content-Security-Policy header.",
                                                cwe_id="CWE-79",
                                                owasp_category="A03:2021 - Injection"
                                            ))
                                else:
                                    async with session.get(form_url, params=form_data, ssl=False) as test_response:
                                        test_html = await test_response.text()
                                        
                                        if XSS_PAYLOADS[0] in test_html:
                                            findings.append(Finding(
                                                title=f"Reflected XSS in Form #{i+1}",
                                                severity="high",
                                                description="Form input is reflected in the response without proper encoding.",
                                                evidence=f"Form at {form_url} reflects XSS payload",
                                                remediation="Implement proper output encoding/escaping for all form inputs. Use Content-Security-Policy header.",
                                                cwe_id="CWE-79",
                                                owasp_category="A03:2021 - Injection"
                                            ))
                            except Exception:
                                pass  # Skip form if submission fails
                
                # Check for inline JavaScript event handlers (DOM-based XSS indicators)
                dangerous_attrs = ['onclick', 'onerror', 'onload', 'onmouseover']
                for attr in dangerous_attrs:
                    elements_with_attr = soup.find_all(attrs={attr: True})
                    if elements_with_attr:
                        findings.append(Finding(
                            title="Potential DOM-based XSS Vector",
                            severity="medium",
                            description=f"Found {len(elements_with_attr)} elements with inline event handler '{attr}'.",
                            evidence=f"Elements with {attr} attribute detected",
                            remediation="Avoid inline event handlers. Use addEventListener in external JavaScript files.",
                            cwe_id="CWE-79",
                            owasp_category="A03:2021 - Injection"
                        ))
                        break  # Only report once
    
    except aiohttp.ClientError as e:
        findings.append(Finding(
            title="XSS Check Connection Error",
            severity="info",
            description="Unable to perform XSS checks due to connection error.",
            evidence=f"Error: {str(e)}",
            remediation="Verify target accessibility.",
            cwe_id=None,
            owasp_category=None
        ))
    
    except Exception as e:
        findings.append(Finding(
            title="XSS Check Error",
            severity="info",
            description="An error occurred during XSS analysis.",
            evidence=f"Error: {str(e)}",
            remediation="Review error and try again.",
            cwe_id=None,
            owasp_category=None
        ))
    
    return findings
