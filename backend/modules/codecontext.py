"""
Module 1: CodeContext
Sends real repo file list to IBM Bob → returns AI-generated architecture analysis.
"""

from bob_client import get_bob


def analyze_code_context(repo_data: dict) -> dict:
    """
    Ask IBM Bob to analyze the repository architecture and tech stack.
    Uses the real file list from GitHub API as context.
    """
    files = repo_data.get('files', [])
    name  = repo_data.get('name', '')
    lang  = repo_data.get('language', 'Unknown')
    desc  = repo_data.get('description', '')

    file_list = '\n'.join(f'  - {f}' for f in files)

    prompt = f"""You are IBM Bob, an expert software architect.

Analyze this GitHub repository and return ONLY valid JSON — no markdown, no explanation outside the JSON.

Repository: {name}
Primary Language: {lang}
Description: {desc}
Files and directories at root level:
{file_list}

Return this exact JSON structure:
{{
  "architecture": "one of: Full-Stack Monolith | REST API / MVC | Frontend SPA | Microservices | Serverless | Backend Service | Library / Package",
  "architectureDescription": "2 sentences explaining the architecture based on the files",
  "techStack": ["list", "of", "detected", "technologies", "frameworks", "tools"],
  "modules": [
    {{"name": "filename or folder", "purpose": "what it does"}}
  ],
  "insights": "2-3 sentences of key observations about this codebase",
  "totalFiles": {len(files)},
  "repoName": "{name}",
  "language": "{lang}"
}}

Base your answer strictly on the file list provided. Be specific and accurate."""

    bob = get_bob()
    result = bob.ask(prompt)

    # Ensure required fields exist as fallback
    result.setdefault('repoName', name)
    result.setdefault('language', lang)
    result.setdefault('totalFiles', len(files))
    result.setdefault('techStack', [lang] if lang else [])
    result.setdefault('modules', [])
    return result
