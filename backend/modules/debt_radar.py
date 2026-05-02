"""
Module 4: Debt Radar - Intelligent Technical Debt Analysis
Uses file analysis and pattern detection to identify technical debt.
NO external AI APIs - pure heuristic-based intelligence.
"""

import requests
from typing import Optional, Dict, List, Tuple
from collections import Counter


def _fetch_file_sizes(owner: str, repo: str, github_token: Optional[str] = None) -> list:
    """Fetch file sizes from GitHub tree API (tries main then master)."""
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if github_token:
        headers['Authorization'] = f'Bearer {github_token}'

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


def _analyze_file_sizes(tree_items: List[Dict]) -> Tuple[List[Dict], int]:
    """
    Analyze file sizes and identify problematic large files.
    Returns: (issues, total_large_files)
    """
    issues = []
    large_files = []
    
    # Exclude binary and generated files
    excluded_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', 
                          '.ttf', '.eot', '.lock', '.min.js', '.min.css', '.map', '.pdf'}
    
    for item in tree_items:
        if item.get('type') != 'blob':
            continue
        
        path = item.get('path', '')
        size = item.get('size', 0)
        
        # Skip excluded files
        if any(path.endswith(ext) for ext in excluded_extensions):
            continue
        
        # Check for large files (>100KB for code files)
        if size > 100000:  # 100KB
            large_files.append((path, size))
            issues.append({
                'type': 'Large File',
                'severity': 'high' if size > 500000 else 'medium',
                'file': path,
                'detail': f'File size is {round(size/1024, 1)}KB, which may impact performance and maintainability',
                'suggestion': 'Consider splitting into smaller modules, lazy loading, or moving to external storage'
            })
    
    return issues, len(large_files)


def _check_missing_tests(files: List[str]) -> List[Dict]:
    """Check for missing test coverage."""
    issues = []
    
    test_patterns = ['test', 'spec', '__tests__', '.test.', '.spec.']
    has_tests = any(any(pattern in f.lower() for pattern in test_patterns) for f in files)
    
    if not has_tests:
        issues.append({
            'type': 'No Test Coverage',
            'severity': 'critical',
            'file': 'N/A',
            'detail': 'No test files detected in repository, indicating zero test coverage',
            'suggestion': 'Implement unit tests using Jest, Pytest, or appropriate framework. Aim for 80%+ coverage'
        })
    else:
        # Check if test coverage is adequate (heuristic: 1 test file per 5 source files)
        source_files = [f for f in files if f.endswith(('.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go'))]
        test_files = [f for f in files if any(pattern in f.lower() for pattern in test_patterns)]
        
        if len(source_files) > 10 and len(test_files) < len(source_files) / 5:
            issues.append({
                'type': 'Low Test Coverage',
                'severity': 'high',
                'file': 'N/A',
                'detail': f'Only {len(test_files)} test files for {len(source_files)} source files (ratio: 1:{len(source_files)//max(len(test_files), 1)})',
                'suggestion': 'Increase test coverage by adding more test files. Target ratio of at least 1:5'
            })
    
    return issues


def _check_documentation(files: List[str]) -> List[Dict]:
    """Check for documentation issues."""
    issues = []
    
    # Check README
    has_readme = any(f.lower().startswith('readme') for f in files)
    if not has_readme:
        issues.append({
            'type': 'Missing README',
            'severity': 'high',
            'file': 'N/A',
            'detail': 'No README file found, making it difficult for developers to understand the project',
            'suggestion': 'Create README.md with project overview, setup instructions, and usage examples'
        })
    
    # Check for docs directory
    has_docs = any('docs/' in f.lower() or 'documentation/' in f.lower() for f in files)
    if not has_docs and len(files) > 30:
        issues.append({
            'type': 'No Documentation Directory',
            'severity': 'medium',
            'file': 'N/A',
            'detail': 'Large project without dedicated documentation directory',
            'suggestion': 'Create docs/ folder with API documentation, architecture guides, and developer notes'
        })
    
    return issues


def _check_ci_cd(files: List[str]) -> List[Dict]:
    """Check for CI/CD configuration."""
    issues = []
    
    ci_patterns = ['.github/workflows', '.gitlab-ci', 'jenkinsfile', '.circleci', '.travis.yml']
    has_ci = any(any(pattern in f.lower() for pattern in ci_patterns) for f in files)
    
    if not has_ci:
        issues.append({
            'type': 'No CI/CD Pipeline',
            'severity': 'high',
            'file': 'N/A',
            'detail': 'No continuous integration or deployment configuration detected',
            'suggestion': 'Set up GitHub Actions, GitLab CI, or Jenkins for automated testing and deployment'
        })
    
    return issues


def _check_dependency_management(files: List[str]) -> List[Dict]:
    """Check dependency management issues."""
    issues = []
    
    # Check for lock files
    lock_files = ['package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'poetry.lock', 'pipfile.lock', 'go.sum']
    has_lock = any(f.lower() in lock_files for f in files)
    has_deps = any(f in ['package.json', 'requirements.txt', 'go.mod', 'cargo.toml'] for f in files)
    
    if has_deps and not has_lock:
        issues.append({
            'type': 'Missing Lock File',
            'severity': 'high',
            'file': 'N/A',
            'detail': 'Dependencies defined but no lock file present, leading to non-reproducible builds',
            'suggestion': 'Commit lock file (package-lock.json, poetry.lock, etc.) to ensure consistent dependencies'
        })
    
    return issues


def _check_security(files: List[str]) -> List[Dict]:
    """Check for security issues."""
    issues = []
    
    # Check for exposed .env
    if '.env' in files:
        issues.append({
            'type': 'Exposed Environment File',
            'severity': 'critical',
            'file': '.env',
            'detail': 'Environment file with secrets is committed to repository',
            'suggestion': 'Remove .env from git immediately, add to .gitignore, rotate all exposed secrets'
        })
    
    # Check for .gitignore
    if '.gitignore' not in files:
        issues.append({
            'type': 'Missing .gitignore',
            'severity': 'medium',
            'file': 'N/A',
            'detail': 'No .gitignore file to prevent committing sensitive or unnecessary files',
            'suggestion': 'Add .gitignore to exclude node_modules, .env, build artifacts, and IDE files'
        })
    
    return issues


def _check_code_quality(files: List[str]) -> List[Dict]:
    """Check for code quality tools."""
    issues = []
    
    quality_files = ['.eslintrc', '.prettierrc', 'pylint', '.flake8', 'tslint.json']
    has_quality = any(any(qf in f.lower() for qf in quality_files) for f in files)
    
    if not has_quality:
        issues.append({
            'type': 'No Code Quality Tools',
            'severity': 'medium',
            'file': 'N/A',
            'detail': 'No linting or formatting configuration detected',
            'suggestion': 'Add ESLint, Prettier, Pylint, or similar tools to maintain code consistency'
        })
    
    return issues


def _check_structure(files: List[str]) -> List[Dict]:
    """Check project structure issues."""
    issues = []
    
    # Check for too many root-level files
    root_files = [f for f in files if '/' not in f and not f.startswith('.')]
    if len(root_files) > 15:
        issues.append({
            'type': 'Cluttered Root Directory',
            'severity': 'low',
            'file': 'N/A',
            'detail': f'{len(root_files)} files in root directory, making navigation difficult',
            'suggestion': 'Organize files into subdirectories (src/, config/, docs/, etc.)'
        })
    
    # Check for duplicate patterns (potential code duplication)
    file_names = [f.split('/')[-1] for f in files]
    name_counts = Counter(file_names)
    duplicates = [name for name, count in name_counts.items() if count > 3 and not name.startswith('.')]
    
    if duplicates:
        issues.append({
            'type': 'Potential Code Duplication',
            'severity': 'medium',
            'file': ', '.join(duplicates[:3]),
            'detail': f'Multiple files with similar names detected: {", ".join(duplicates[:3])}',
            'suggestion': 'Review for code duplication and consider extracting common logic into shared modules'
        })
    
    return issues


def _calculate_debt_score(issues: List[Dict]) -> Tuple[int, str]:
    """
    Calculate technical debt score (0-100, where 100 is worst).
    Returns: (score, level)
    """
    score = 0
    
    severity_weights = {
        'critical': 25,
        'high': 15,
        'medium': 8,
        'low': 3
    }
    
    for issue in issues:
        severity = issue.get('severity', 'low')
        score += severity_weights.get(severity, 3)
    
    # Cap at 100
    score = min(100, score)
    
    # Determine level
    if score >= 75:
        level = "Critical"
    elif score >= 50:
        level = "High"
    elif score >= 25:
        level = "Medium"
    else:
        level = "Low"
    
    return score, level


def _generate_suggestions(issues: List[Dict]) -> List[str]:
    """Generate prioritized action items."""
    suggestions = []
    
    # Prioritize critical issues
    critical = [i for i in issues if i.get('severity') == 'critical']
    high = [i for i in issues if i.get('severity') == 'high']
    
    if critical:
        suggestions.append(f"🚨 URGENT: Address {len(critical)} critical security/quality issues immediately")
    
    if high:
        suggestions.append(f"⚠️ HIGH PRIORITY: Resolve {len(high)} high-severity technical debt items")
    
    # Specific recommendations
    issue_types = set(i.get('type') for i in issues)
    
    if 'No Test Coverage' in issue_types:
        suggestions.append("Implement comprehensive test suite to ensure code reliability")
    
    if 'No CI/CD Pipeline' in issue_types:
        suggestions.append("Set up automated CI/CD pipeline for consistent deployments")
    
    if 'Missing README' in issue_types or 'No Documentation Directory' in issue_types:
        suggestions.append("Improve documentation to enhance developer onboarding and maintenance")
    
    if 'Large File' in issue_types:
        suggestions.append("Refactor large files into smaller, more maintainable modules")
    
    if not suggestions:
        suggestions.append("Continue maintaining good code quality and best practices")
    
    return suggestions[:5]  # Top 5 suggestions


def analyze_debt_radar(repo_data: dict, github_token: Optional[str] = None) -> dict:
    """
    Intelligent technical debt analysis using file analysis and heuristics.
    NO AI APIs - pure logic-based intelligence.
    """
    files = repo_data.get('files', [])
    name = repo_data.get('name', 'Unknown')
    owner = repo_data.get('owner', '')
    repo = repo_data.get('repo', '')
    
    all_issues = []
    
    # Fetch file sizes if possible
    tree_items = []
    if owner and repo:
        tree_items = _fetch_file_sizes(owner, repo, github_token)
        size_issues, _ = _analyze_file_sizes(tree_items)
        all_issues.extend(size_issues)
    
    # Run all checks
    all_issues.extend(_check_missing_tests(files))
    all_issues.extend(_check_documentation(files))
    all_issues.extend(_check_ci_cd(files))
    all_issues.extend(_check_dependency_management(files))
    all_issues.extend(_check_security(files))
    all_issues.extend(_check_code_quality(files))
    all_issues.extend(_check_structure(files))
    
    # Calculate score and level
    debt_score, debt_level = _calculate_debt_score(all_issues)
    
    # Count by severity
    severity_counts = {
        'critical': len([i for i in all_issues if i.get('severity') == 'critical']),
        'high': len([i for i in all_issues if i.get('severity') == 'high']),
        'medium': len([i for i in all_issues if i.get('severity') == 'medium']),
        'low': len([i for i in all_issues if i.get('severity') == 'low'])
    }
    
    # Generate suggestions
    suggestions = _generate_suggestions(all_issues)
    
    return {
        'debtScore': debt_score,
        'debtLevel': debt_level,
        'totalIssues': len(all_issues),
        'severityCounts': severity_counts,
        'issues': all_issues,
        'suggestions': suggestions,
        'repoName': name,
        'filesAnalyzed': len(files) + len(tree_items)
    }

# Made with Bob
