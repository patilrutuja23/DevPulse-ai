"""
Module 2: PR Guardian
Sends real repo file list to IBM Bob → returns AI-generated health check and PR readiness.
"""

from bob_client import get_bob


def analyze_pr_guardian(repo_data: dict) -> dict:
    """
    Ask IBM Bob to review repository health and PR readiness.
    Uses the real file list from GitHub API as context.
    """
    files      = repo_data.get('files', [])
    name       = repo_data.get('name', '')
    lang       = repo_data.get('language', 'Unknown')
    open_issues = repo_data.get('open_issues', 0)

    file_list = '\n'.join(f'  - {f}' for f in files)

    prompt = f"""You are IBM Bob, an expert code reviewer and DevOps engineer.

Review this repository for PR readiness and health issues. Return ONLY valid JSON.

Repository: {name}
Language: {lang}
Open Issues: {open_issues}
Root-level files and folders:
{file_list}

Analyze for: README, tests, CI/CD config, .gitignore, .env exposure, license, lock files, security risks.

Return this exact JSON:
{{
  "score": <integer 0-100>,
  "verdict": "Good | Needs Improvement | Poor",
  "verdictColor": "green | yellow | red",
  "issues": [
    {{
      "severity": "critical | high | medium | low",
      "check": "short name",
      "message": "what is wrong",
      "suggestion": "how to fix it"
    }}
  ],
  "passed": [
    {{
      "check": "short name",
      "message": "what looks good"
    }}
  ],
  "totalChecks": <number>,
  "issueCount": <number>,
  "passedCount": <number>
}}

Score starts at 100. Deduct: critical=25, high=15, medium=8, low=3.
Be specific — reference actual filenames from the list above."""

    bob = get_bob()
    result = bob.ask(prompt)

    # Ensure required fields
    result.setdefault('issues', [])
    result.setdefault('passed', [])
    result.setdefault('score', 50)
    result.setdefault('verdict', 'Needs Improvement')
    result.setdefault('verdictColor', 'yellow')
    result['issueCount']  = len(result['issues'])
    result['passedCount'] = len(result['passed'])
    result['totalChecks'] = result['issueCount'] + result['passedCount']
    return result
