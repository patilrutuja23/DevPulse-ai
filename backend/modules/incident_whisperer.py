"""
Module 3: Incident Whisperer - Intelligent Bug Analysis & Debugging
Uses pattern matching and error analysis to diagnose bugs.
NO external AI APIs - pure logic-based debugging intelligence.
"""

import re
from typing import Dict, List, Tuple


def _detect_error_type(error_message: str, code_snippet: str) -> Tuple[str, str]:
    """
    Detect error type and severity from error message patterns.
    Returns: (error_type, severity)
    """
    error_lower = error_message.lower()
    code_lower = code_snippet.lower()
    
    # Critical errors
    if any(pattern in error_lower for pattern in ['segmentation fault', 'memory', 'stack overflow', 'out of memory']):
        return "Memory Error", "critical"
    
    if 'security' in error_lower or 'vulnerability' in error_lower:
        return "Security Error", "critical"
    
    # High severity errors
    if any(pattern in error_lower for pattern in ['undefined', 'is not defined', 'cannot read property', 'cannot read properties']):
        return "JavaScript Runtime Error", "high"
    
    if any(pattern in error_lower for pattern in ['nameerror', 'attributeerror', 'keyerror']):
        return "Python Runtime Error", "high"
    
    if 'typeerror' in error_lower:
        return "Type Error", "high"
    
    # Medium severity
    if any(pattern in error_lower for pattern in ['promise', 'async', 'await', 'unhandled rejection']):
        return "Async/Promise Error", "medium"
    
    if any(pattern in error_lower for pattern in ['network', 'fetch', 'request', 'timeout', 'cors']):
        return "Network Error", "medium"
    
    if any(pattern in error_lower for pattern in ['import', 'module', 'cannot find']):
        return "Import Error", "medium"
    
    if 'syntax' in error_lower:
        return "Syntax Error", "high"
    
    # Default
    return "Runtime Error", "medium"


def _analyze_undefined_error(error_message: str, code_snippet: str) -> Dict:
    """Analyze undefined variable/property errors."""
    # Extract variable name
    match = re.search(r"'(\w+)' is not defined|(\w+) is not defined|Cannot read propert(?:y|ies) of undefined", error_message)
    var_name = match.group(1) or match.group(2) if match else "variable"
    
    root_cause = f"Variable or property '{var_name}' is accessed before being defined or initialized"
    
    explanation = (
        f"The error occurs because '{var_name}' is being used in the code but hasn't been declared, "
        f"initialized, or is out of scope. This commonly happens with typos, missing imports, "
        f"or accessing properties on null/undefined objects."
    )
    
    fix = (
        f"1. Check if '{var_name}' is spelled correctly\n"
        f"2. Ensure '{var_name}' is declared before use (let, const, var)\n"
        f"3. If it's an import, verify the import statement\n"
        f"4. Add null/undefined checks before accessing properties"
    )
    
    # Generate fixed code
    updated_code = code_snippet
    if 'const' not in code_snippet and 'let' not in code_snippet and 'var' not in code_snippet:
        # Add declaration
        updated_code = f"const {var_name} = null; // Initialize variable\n{code_snippet}"
    
    # Add null check if accessing properties
    if '.' in code_snippet:
        updated_code = f"if ({var_name}) {{\n  {code_snippet}\n}}"
    
    reproduction_steps = [
        f"Run the code without declaring '{var_name}'",
        f"Attempt to access '{var_name}' in the current scope",
        "Observe the undefined error"
    ]
    
    return {
        'rootCause': root_cause,
        'explanation': explanation,
        'fix': fix,
        'updatedCode': updated_code,
        'reproductionSteps': reproduction_steps
    }


def _analyze_type_error(error_message: str, code_snippet: str) -> Dict:
    """Analyze type-related errors."""
    root_cause = "Operation attempted on incompatible data type"
    
    explanation = (
        "This error occurs when trying to perform an operation on a value of the wrong type, "
        "such as calling a method on null/undefined, treating a string as a number, "
        "or accessing array methods on non-arrays."
    )
    
    fix = (
        "1. Add type checking before operations (typeof, instanceof)\n"
        "2. Use optional chaining (?.) for safe property access\n"
        "3. Validate input types at function boundaries\n"
        "4. Use TypeScript for compile-time type safety"
    )
    
    # Add type guards
    updated_code = f"""// Add type checking
if (typeof value !== 'undefined' && value !== null) {{
  {code_snippet}
}}"""
    
    reproduction_steps = [
        "Pass incorrect type to function or method",
        "Attempt operation on null/undefined value",
        "Observe type error"
    ]
    
    return {
        'rootCause': root_cause,
        'explanation': explanation,
        'fix': fix,
        'updatedCode': updated_code,
        'reproductionSteps': reproduction_steps
    }


def _analyze_async_error(error_message: str, code_snippet: str) -> Dict:
    """Analyze async/promise errors."""
    root_cause = "Unhandled promise rejection or improper async/await usage"
    
    explanation = (
        "This error occurs when a Promise is rejected but no .catch() handler is provided, "
        "or when async operations are not properly awaited. This can lead to race conditions "
        "and unexpected behavior in asynchronous code."
    )
    
    fix = (
        "1. Add .catch() handlers to all promises\n"
        "2. Use try-catch blocks with async/await\n"
        "3. Ensure all async functions are awaited\n"
        "4. Add error boundaries for React components"
    )
    
    # Add proper error handling
    if 'async' in code_snippet or 'await' in code_snippet:
        updated_code = f"""async function handleAsync() {{
  try {{
    {code_snippet}
  }} catch (error) {{
    console.error('Error:', error);
    // Handle error appropriately
  }}
}}"""
    else:
        updated_code = f"""{code_snippet}
  .catch(error => {{
    console.error('Promise rejected:', error);
    // Handle error appropriately
  }});"""
    
    reproduction_steps = [
        "Execute async operation without error handling",
        "Trigger a rejection or error in the promise",
        "Observe unhandled rejection warning"
    ]
    
    return {
        'rootCause': root_cause,
        'explanation': explanation,
        'fix': fix,
        'updatedCode': updated_code,
        'reproductionSteps': reproduction_steps
    }


def _analyze_import_error(error_message: str, code_snippet: str) -> Dict:
    """Analyze import/module errors."""
    # Extract module name
    match = re.search(r"Cannot find module '([^']+)'|No module named '([^']+)'", error_message)
    module_name = match.group(1) or match.group(2) if match else "module"
    
    root_cause = f"Module '{module_name}' is not installed or path is incorrect"
    
    explanation = (
        f"The error occurs because the module '{module_name}' cannot be found. "
        f"This typically means the package is not installed, the import path is wrong, "
        f"or there's a typo in the module name."
    )
    
    fix = (
        f"1. Install the module: npm install {module_name} (or pip install {module_name})\n"
        f"2. Check the import path is correct\n"
        f"3. Verify the module name spelling\n"
        f"4. Ensure package.json/requirements.txt includes the dependency"
    )
    
    updated_code = f"""// First install: npm install {module_name}
{code_snippet}"""
    
    reproduction_steps = [
        f"Remove '{module_name}' from node_modules or site-packages",
        "Run the code with the import statement",
        "Observe module not found error"
    ]
    
    return {
        'rootCause': root_cause,
        'explanation': explanation,
        'fix': fix,
        'updatedCode': updated_code,
        'reproductionSteps': reproduction_steps
    }


def _analyze_syntax_error(error_message: str, code_snippet: str) -> Dict:
    """Analyze syntax errors."""
    root_cause = "Invalid syntax in code"
    
    explanation = (
        "Syntax errors occur when code violates the language's grammatical rules. "
        "Common causes include missing brackets, unclosed strings, invalid operators, "
        "or incorrect indentation (Python)."
    )
    
    fix = (
        "1. Check for missing or extra brackets/parentheses\n"
        "2. Ensure all strings are properly closed\n"
        "3. Verify correct indentation (Python)\n"
        "4. Use a linter (ESLint, Pylint) to catch syntax issues"
    )
    
    # Try to fix common syntax issues
    updated_code = code_snippet
    
    # Balance brackets
    open_count = code_snippet.count('(') - code_snippet.count(')')
    if open_count > 0:
        updated_code += ')' * open_count
    
    reproduction_steps = [
        "Write code with syntax error",
        "Attempt to run or compile",
        "Observe syntax error message"
    ]
    
    return {
        'rootCause': root_cause,
        'explanation': explanation,
        'fix': fix,
        'updatedCode': updated_code,
        'reproductionSteps': reproduction_steps
    }


def _analyze_network_error(error_message: str, code_snippet: str) -> Dict:
    """Analyze network/API errors."""
    root_cause = "Network request failed or API endpoint unreachable"
    
    explanation = (
        "Network errors occur when HTTP requests fail due to connectivity issues, "
        "CORS restrictions, incorrect URLs, timeout, or server errors. "
        "These are common in frontend applications making API calls."
    )
    
    fix = (
        "1. Verify the API endpoint URL is correct\n"
        "2. Check CORS configuration on the server\n"
        "3. Add timeout and retry logic\n"
        "4. Implement proper error handling for failed requests\n"
        "5. Check network connectivity and firewall settings"
    )
    
    updated_code = f"""// Add robust error handling
try {{
  const response = await fetch(url, {{
    method: 'GET',
    headers: {{ 'Content-Type': 'application/json' }},
    timeout: 5000
  }});
  
  if (!response.ok) {{
    throw new Error(`HTTP error! status: ${{response.status}}`);
  }}
  
  const data = await response.json();
  return data;
}} catch (error) {{
  console.error('Network request failed:', error);
  // Implement retry logic or fallback
  return null;
}}"""
    
    reproduction_steps = [
        "Make request to invalid or unreachable endpoint",
        "Observe network error or timeout",
        "Check browser console for details"
    ]
    
    return {
        'rootCause': root_cause,
        'explanation': explanation,
        'fix': fix,
        'updatedCode': updated_code,
        'reproductionSteps': reproduction_steps
    }


def analyze_incident(error_message: str, code_snippet: str) -> dict:
    """
    Intelligent bug analysis using pattern matching and error classification.
    NO AI APIs - pure logic-based debugging intelligence.
    """
    # Detect error type and severity
    error_type, severity = _detect_error_type(error_message, code_snippet)
    
    # Route to appropriate analyzer
    error_lower = error_message.lower()
    
    if 'undefined' in error_lower or 'is not defined' in error_lower:
        analysis = _analyze_undefined_error(error_message, code_snippet)
    elif 'type' in error_lower and 'error' in error_lower:
        analysis = _analyze_type_error(error_message, code_snippet)
    elif any(kw in error_lower for kw in ['promise', 'async', 'await']):
        analysis = _analyze_async_error(error_message, code_snippet)
    elif 'import' in error_lower or 'module' in error_lower:
        analysis = _analyze_import_error(error_message, code_snippet)
    elif 'syntax' in error_lower:
        analysis = _analyze_syntax_error(error_message, code_snippet)
    elif 'network' in error_lower or 'fetch' in error_lower:
        analysis = _analyze_network_error(error_message, code_snippet)
    else:
        # Generic analysis
        analysis = {
            'rootCause': 'Runtime error in code execution',
            'explanation': 'An error occurred during code execution. Review the error message and stack trace for specific details.',
            'fix': '1. Check the error message for clues\n2. Review recent code changes\n3. Add logging to trace execution\n4. Use debugger to step through code',
            'updatedCode': f"// Add error handling\ntry {{\n  {code_snippet}\n}} catch (error) {{\n  console.error('Error:', error);\n}}",
            'reproductionSteps': ['Execute the code', 'Observe the error', 'Review error details']
        }
    
    # Add error type and severity
    analysis['errorType'] = error_type
    analysis['severity'] = severity
    analysis['errorMessage'] = error_message
    
    return analysis

# Made with Bob
