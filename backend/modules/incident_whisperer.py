"""
Module 3: Incident Whisperer
Sends error message + code snippet to IBM Bob → returns AI-powered root cause analysis.
"""

from bob_client import get_bob


def analyze_incident(error_message: str, code_snippet: str) -> dict:
    """
    Ask IBM Bob to diagnose a bug from an error message and code snippet.
    Returns root cause, explanation, fix, updated code, and reproduction steps.
    """
    prompt = f"""You are IBM Bob, an expert debugging engineer.

Analyze this bug and return ONLY valid JSON — no markdown, no text outside the JSON.

ERROR MESSAGE:
{error_message}

CODE SNIPPET:
{code_snippet}

Diagnose the bug and return this exact JSON:
{{
  "rootCause": "one sentence — the exact root cause",
  "explanation": "2-3 sentences explaining why this error occurs and what triggers it",
  "fix": "clear, specific instructions on how to fix the bug",
  "updatedCode": "the corrected version of the code snippet with the fix applied",
  "reproductionSteps": [
    "step 1 to reproduce the bug",
    "step 2",
    "step 3"
  ],
  "errorType": "JavaScript Runtime Error | Python Runtime Error | Async/Promise Error | Network Error | Import Error | Runtime Error",
  "severity": "critical | high | medium | low"
}}

Be precise. The updatedCode must be a working fixed version of the snippet provided."""

    bob = get_bob()
    result = bob.ask(prompt)

    # Ensure required fields
    result.setdefault('rootCause', 'Could not determine root cause')
    result.setdefault('explanation', '')
    result.setdefault('fix', '')
    result.setdefault('updatedCode', code_snippet)
    result.setdefault('reproductionSteps', [])
    result.setdefault('errorType', 'Runtime Error')
    result.setdefault('severity', 'medium')
    return result
