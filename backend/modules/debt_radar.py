"""
Module 4: Debt Radar
Sends real repo file list + sizes to IBM Bob → returns AI-powered technical debt analysis.
"""

import requests
from typing import Optional
from bob_client import get_bob


def _fetch_file_sizes(owner: str, repo: str, github_token: Optional[str] = None) -> list:
    """Fetch file sizes from GitHub tree API (tries main then master)."""
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    for branch in ('main', 'master'):
        try:
            resp = requests.get(
                f'https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1',
                headers=headers, timeout=15
            )
            if resp.status_code == 200:
                return resp.json().get('tree', [])
        except Exception:
            pass
    return []


def analyze_debt_radar(repo_data: dict, github_token: Optional[str] = None) -> dict:
    """
    Ask IBM Bob to analyze technical debt using the real file list and sizes.
    """
    files  = repo_data.get('files', [])
    name   = repo_data.get('name', '')
    lang   = repo_data.get('language', 'Unknown')
    owner  = repo_data.get('owner', '')
    repo   = repo_data.get('repo', '')

    # Fetch real file sizes from GitHub
    size_map = {}
    if owner and repo:
        tree_items = _fetch_file_sizes(owner, repo, github_token)
        for item in tree_items:
            if item.get('type') == 'blob':
                size_map[item['path']] = item.get('size', 0)

    # Build annotated file list with sizes
    file_lines = []
    for f in files:
        size = size_map.get(f)
        if size is not None:
            kb = round(size / 1024, 1)
            file_lines.append(f'  - {f}  ({kb} KB)')
        else:
            file_lines.append(f'  - {f}')

    # Also include large nested files from tree
    large_files = [
        f'  - {item["path"]}  ({round(item["size"]/1024, 1)} KB)'
        for item in (tree_items if owner and repo else [])
        if item.get('type') == 'blob'
        and item.get('size', 0) > 8000
        and not any(item['path'].endswith(ext) for ext in ('.png','.jpg','.gif','.svg','.ico','.woff','.ttf','.lock','.min.js','.min.css'))
    ]

    file_context = '\n'.join(file_lines)
    if large_files:
        file_context += '\n\nLarge files detected:\n' + '\n'.join(large_files[:20])

    prompt = f"""You are IBM Bob, an expert software architect specializing in technical debt.

Analyze this repository for technical debt. Return ONLY valid JSON.

Repository: {name}
Language: {lang}
Files and sizes:
{file_context}

Identify: large files, missing tests, no CI/CD, missing docs, no lock file, .env committed, config sprawl, duplicate patterns, outdated dependencies, poor structure.

Return this exact JSON:
{{
  "debtScore": <integer 0-100, where 0=no debt, 100=worst>,
  "debtLevel": "Low | Medium | High | Critical",
  "totalIssues": <number>,
  "severityCounts": {{
    "critical": <number>,
    "high": <number>,
    "medium": <number>,
    "low": <number>
  }},
  "issues": [
    {{
      "type": "issue category name",
      "severity": "critical | high | medium | low",
      "file": "specific filename or path",
      "detail": "what the problem is",
      "suggestion": "how to fix it"
    }}
  ],
  "suggestions": ["top prioritized action items as strings"]
}}

Reference actual filenames. Be specific about what you see in the file list."""

    bob = get_bob()
    result = bob.ask(prompt)

    # Ensure required fields
    result.setdefault('debtScore', 0)
    result.setdefault('debtLevel', 'Low')
    result.setdefault('totalIssues', 0)
    result.setdefault('severityCounts', {'critical': 0, 'high': 0, 'medium': 0, 'low': 0})
    result.setdefault('issues', [])
    result.setdefault('suggestions', [])
    result['totalIssues'] = len(result['issues'])
    return result
