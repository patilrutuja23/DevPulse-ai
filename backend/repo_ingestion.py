"""
GitHub Repository Ingestion Module
Fetches repository metadata and file list from GitHub API
"""

import os
import re
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse


# File extensions to include
SUPPORTED_EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go', '.rs', '.cpp', '.c', '.h', '.hpp',
                         '.css', '.html', '.json', '.md', '.yml', '.yaml', '.toml', '.env', '.txt'}

# Directories to exclude
EXCLUDED_DIRS = {
    'node_modules', '.git', '__pycache__', 'venv', 'env',
    'dist', 'build', 'target', '.next', '.nuxt', 'coverage',
    '.pytest_cache', '.mypy_cache', 'vendor', 'packages'
}

# Configuration
MAX_FILES = 50
MAX_FILE_SIZE = 2000  # characters


def parse_github_url(repo_url: str) -> tuple[str, str]:
    """
    Parse GitHub repository URL to extract owner and repo name.
    
    Supports formats:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo.git
    
    Args:
        repo_url: GitHub repository URL
    
    Returns:
        Tuple of (owner, repo_name)
    
    Raises:
        ValueError: If URL format is invalid
    """
    # Handle git@ format
    if repo_url.startswith('git@github.com:'):
        match = re.match(r'git@github\.com:([^/]+)/(.+?)(?:\.git)?$', repo_url)
        if match:
            return match.group(1), match.group(2)
    
    # Handle https format
    parsed = urlparse(repo_url)
    if parsed.netloc == 'github.com':
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo = path_parts[1].replace('.git', '')
            return owner, repo
    
    raise ValueError(f"Invalid GitHub URL format: {repo_url}")


def load_repo(repo_url: str, github_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Load repository metadata and file list from GitHub API.
    Returns name, description, stars, language, and files list.
    """
    try:
        owner, repo = parse_github_url(repo_url)
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if github_token:
            headers['Authorization'] = f'token {github_token}'

        # Fetch repo metadata
        meta_resp = requests.get(
            f'https://api.github.com/repos/{owner}/{repo}',
            headers=headers, timeout=10
        )
        meta_resp.raise_for_status()
        meta = meta_resp.json()

        # Fetch root contents for file list
        contents_resp = requests.get(
            f'https://api.github.com/repos/{owner}/{repo}/contents',
            headers=headers, timeout=10
        )
        contents_resp.raise_for_status()
        contents = contents_resp.json()

        files = [
            item['name'] for item in contents
            if item['type'] in ('file', 'dir')
        ]

        return {
            'name': meta.get('name', repo),
            'description': meta.get('description') or 'No description provided',
            'stars': meta.get('stargazers_count', 0),
            'language': meta.get('language') or 'Unknown',
            'owner': owner,
            'repo': repo,
            'files': files,
            'full_name': meta.get('full_name', f'{owner}/{repo}'),
            'default_branch': meta.get('default_branch', 'main'),
            'open_issues': meta.get('open_issues_count', 0),
            'forks': meta.get('forks_count', 0),
        }

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else 0
        if status == 404:
            return {'error': f'Repository not found: {repo_url}'}
        if status == 403:
            return {'error': 'GitHub API rate limit exceeded. Add a GITHUB_TOKEN to .env'}
        return {'error': f'GitHub API error: {str(e)}'}
    except ValueError as e:
        return {'error': str(e)}
    except Exception as e:
        return {'error': f'Failed to load repository: {str(e)}'}


def should_include_file(file_path: str) -> bool:
    """
    Check if a file should be included based on extension and path.
    
    Args:
        file_path: Path to the file
    
    Returns:
        True if file should be included, False otherwise
    """
    # Check if any excluded directory is in the path
    path_parts = file_path.split('/')
    if any(excluded in path_parts for excluded in EXCLUDED_DIRS):
        return False
    
    # Check file extension
    _, ext = os.path.splitext(file_path)
    return ext.lower() in SUPPORTED_EXTENSIONS


def fetch_file_content(owner: str, repo: str, file_path: str, github_token: Optional[str] = None) -> str:
    """
    Fetch content of a single file from GitHub.
    
    Args:
        owner: Repository owner
        repo: Repository name
        file_path: Path to file in repository
        github_token: GitHub personal access token
    
    Returns:
        File content (truncated if too large)
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    headers = {'Accept': 'application/vnd.github.v3.raw'}
    
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        content = response.text
        
        # Truncate if too large
        if len(content) > MAX_FILE_SIZE:
            content = content[:MAX_FILE_SIZE] + "\n\n... [truncated]"
        
        return content
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching file: {str(e)}"


def fetch_repo_tree(owner: str, repo: str, github_token: Optional[str] = None) -> List[str]:
    """
    Fetch the complete file tree of a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        github_token: GitHub personal access token
    
    Returns:
        List of file paths in the repository
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    headers = {}
    
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        # Try 'master' branch if 'main' fails
        if response.status_code == 404:
            url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
            response = requests.get(url, headers=headers, timeout=15)
        
        response.raise_for_status()
        data = response.json()
        
        # Extract file paths (exclude directories)
        tree = data.get('tree', [])
        file_paths = [
            item['path'] 
            for item in tree 
            if item['type'] == 'blob' and should_include_file(item['path'])
        ]
        
        return file_paths[:MAX_FILES]  # Limit to MAX_FILES
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repository tree: {str(e)}")
        return []


def fetch_repo_context(repo_url: str, github_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch complete repository context including file tree and contents.
    
    This is the main function that orchestrates the repository ingestion process.
    
    Args:
        repo_url: GitHub repository URL (e.g., "https://github.com/user/repo")
        github_token: GitHub personal access token (optional, but recommended for rate limits)
    
    Returns:
        Dictionary containing:
        - files: List of dicts with 'path' and 'content' keys
        - tree: List of all file paths
        - total_files: Total number of files processed
        - repo_url: Original repository URL
        - error: Error message if something went wrong
    
    Example:
        >>> context = fetch_repo_context("https://github.com/user/repo", "ghp_token")
        >>> print(f"Loaded {context['total_files']} files")
        >>> for file in context['files']:
        ...     print(f"  - {file['path']}")
    """
    try:
        # Parse GitHub URL
        owner, repo = parse_github_url(repo_url)
        print(f"Fetching repository: {owner}/{repo}")
        
        # Fetch file tree
        file_paths = fetch_repo_tree(owner, repo, github_token)
        
        if not file_paths:
            return {
                "error": "No files found or unable to access repository",
                "files": [],
                "tree": [],
                "total_files": 0,
                "repo_url": repo_url
            }
        
        print(f"Found {len(file_paths)} relevant files")
        
        # Fetch content for each file
        files_with_content = []
        for i, file_path in enumerate(file_paths, 1):
            print(f"  [{i}/{len(file_paths)}] Fetching: {file_path}")
            content = fetch_file_content(owner, repo, file_path, github_token)
            files_with_content.append({
                "path": file_path,
                "content": content
            })
        
        return {
            "files": files_with_content,
            "tree": file_paths,
            "total_files": len(file_paths),
            "repo_url": repo_url,
            "owner": owner,
            "repo": repo
        }
    
    except ValueError as e:
        return {
            "error": str(e),
            "files": [],
            "tree": [],
            "total_files": 0,
            "repo_url": repo_url
        }
    
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "files": [],
            "tree": [],
            "total_files": 0,
            "repo_url": repo_url
        }


def get_repo_stats(repo_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate statistics about the fetched repository.
    
    Args:
        repo_context: Repository context from fetch_repo_context()
    
    Returns:
        Dictionary with repository statistics
    """
    if "error" in repo_context:
        return {"error": repo_context["error"]}
    
    # Count files by extension
    extension_counts = {}
    total_lines = 0
    total_chars = 0
    
    for file_info in repo_context.get("files", []):
        # Extension
        _, ext = os.path.splitext(file_info["path"])
        ext = ext.lower() or "no_extension"
        extension_counts[ext] = extension_counts.get(ext, 0) + 1
        
        # Lines and characters
        content = file_info["content"]
        total_lines += content.count('\n')
        total_chars += len(content)
    
    return {
        "total_files": repo_context.get("total_files", 0),
        "extensions": extension_counts,
        "total_lines": total_lines,
        "total_characters": total_chars,
        "average_file_size": total_chars // max(repo_context.get("total_files", 1), 1)
    }


if __name__ == "__main__":
    # Test the module
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Get test repository from command line or environment
    test_repo = sys.argv[1] if len(sys.argv) > 1 else os.getenv("DEMO_REPO_URL")
    github_token = os.getenv("GITHUB_TOKEN")
    
    if not test_repo:
        print("Usage: python repo_ingestion.py <github_repo_url>")
        print("Or set DEMO_REPO_URL in .env file")
        sys.exit(1)
    
    print(f"Testing repository ingestion for: {test_repo}")
    print("="*60)
    
    # Fetch repository context
    context = fetch_repo_context(test_repo, github_token)
    
    # Display results
    if "error" in context:
        print(f"❌ Error: {context['error']}")
    else:
        print(f"✅ Successfully fetched repository context")
        print(f"\nRepository: {context['repo_url']}")
        print(f"Total files: {context['total_files']}")
        print(f"\nFile tree:")
        for path in context['tree'][:10]:
            print(f"  - {path}")
        if context['total_files'] > 10:
            print(f"  ... and {context['total_files'] - 10} more files")
        
        # Show statistics
        stats = get_repo_stats(context)
        print(f"\nStatistics:")
        print(f"  Total lines: {stats['total_lines']}")
        print(f"  Total characters: {stats['total_characters']}")
        print(f"  Average file size: {stats['average_file_size']} chars")
        print(f"\nFiles by extension:")
        for ext, count in sorted(stats['extensions'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {ext}: {count} files")

# Made with Bob
