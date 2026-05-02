"""
Module 2: PR Guardian - Intelligent Repository Health Analysis
Uses advanced scoring algorithms and pattern detection for PR readiness.
NO external AI APIs - pure heuristic-based intelligence.
"""

from typing import Dict, List, Any


def _calculate_health_score(issues: List[Dict]) -> tuple[int, str, str]:
    """
    Calculate health score based on issue severity.
    Returns: (score, verdict, color)
    """
    score = 100
    
    severity_deductions = {
        'critical': 25,
        'high': 15,
        'medium': 8,
        'low': 3
    }
    
    for issue in issues:
        severity = issue.get('severity', 'low')
        score -= severity_deductions.get(severity, 3)
    
    score = max(0, score)  # Don't go below 0
    
    # Determine verdict
    if score >= 80:
        return score, "Good", "green"
    elif score >= 60:
        return score, "Needs Improvement", "yellow"
    else:
        return score, "Poor", "red"


def _check_readme(files: List[str]) -> Dict | None:
    """Check for README file."""
    readme_files = [f for f in files if f.lower().startswith('readme')]
    
    if not readme_files:
        return {
            'severity': 'high',
            'check': 'README Missing',
            'message': 'No README file found in repository',
            'suggestion': 'Add a README.md with project description, setup instructions, and usage examples',
            'impact': 'Increases onboarding time for new developers and reduces project discoverability'
        }
    return None


def _check_tests(files: List[str]) -> Dict | None:
    """Check for test files."""
    test_patterns = ['test', 'spec', '__tests__', '.test.', '.spec.']
    has_tests = any(any(pattern in f.lower() for pattern in test_patterns) for f in files)
    
    if not has_tests:
        return {
            'severity': 'high',
            'check': 'No Tests',
            'message': 'No test files detected in repository',
            'suggestion': 'Add unit tests using Jest, Pytest, or appropriate testing framework',
            'impact': 'Significantly increases risk of production bugs and makes refactoring dangerous'
        }
    return None


def _check_gitignore(files: List[str]) -> Dict | None:
    """Check for .gitignore file."""
    if '.gitignore' not in files:
        return {
            'severity': 'medium',
            'check': 'Missing .gitignore',
            'message': 'No .gitignore file found',
            'suggestion': 'Add .gitignore to exclude node_modules, .env, build artifacts, and IDE files',
            'impact': 'May lead to committing sensitive files, dependencies, or build artifacts'
        }
    return None


def _check_env_exposure(files: List[str]) -> Dict | None:
    """Check if .env file is committed (security risk)."""
    if '.env' in files:
        return {
            'severity': 'critical',
            'check': 'Environment File Exposed',
            'message': '.env file is committed to repository',
            'suggestion': 'Remove .env from git, add to .gitignore, and use .env.example instead',
            'impact': 'CRITICAL SECURITY RISK: Exposes API keys, passwords, and secrets to public'
        }
    return None


def _check_license(files: List[str]) -> Dict | None:
    """Check for LICENSE file."""
    license_files = [f for f in files if f.lower().startswith('license')]
    
    if not license_files:
        return {
            'severity': 'low',
            'check': 'No License',
            'message': 'No LICENSE file found',
            'suggestion': 'Add a LICENSE file (MIT, Apache 2.0, GPL, etc.) to clarify usage rights',
            'impact': 'Legal ambiguity may prevent others from using or contributing to the project'
        }
    return None


def _check_ci_cd(files: List[str]) -> Dict | None:
    """Check for CI/CD configuration."""
    ci_patterns = ['.github/workflows', '.gitlab-ci', 'jenkinsfile', '.circleci', '.travis.yml']
    has_ci = any(any(pattern in f.lower() for pattern in ci_patterns) for f in files)
    
    if not has_ci:
        return {
            'severity': 'medium',
            'check': 'No CI/CD',
            'message': 'No continuous integration configuration detected',
            'suggestion': 'Set up GitHub Actions, GitLab CI, or Jenkins for automated testing and deployment',
            'impact': 'Manual testing and deployment increases error risk and slows down releases'
        }
    return None


def _check_dependencies(files: List[str]) -> Dict | None:
    """Check for dependency lock files."""
    lock_files = ['package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'poetry.lock', 'pipfile.lock', 'go.sum', 'cargo.lock']
    has_lock = any(f.lower() in lock_files for f in files)
    has_deps = any(f in ['package.json', 'requirements.txt', 'go.mod', 'cargo.toml', 'pyproject.toml'] for f in files)
    
    if has_deps and not has_lock:
        return {
            'severity': 'medium',
            'check': 'No Lock File',
            'message': 'Dependency file found but no lock file',
            'suggestion': 'Commit lock file (package-lock.json, poetry.lock, etc.) to ensure reproducible builds',
            'impact': 'Builds may fail or behave differently across environments due to version mismatches'
        }
    return None


def _check_documentation(files: List[str]) -> Dict | None:
    """Check for documentation."""
    doc_patterns = ['docs/', 'documentation/', 'wiki/']
    has_docs = any(any(pattern in f.lower() for pattern in doc_patterns) for f in files)
    
    if not has_docs and len(files) > 20:
        return {
            'severity': 'low',
            'check': 'Limited Documentation',
            'message': 'No dedicated documentation directory found',
            'suggestion': 'Create a docs/ folder with API documentation, architecture diagrams, and guides'
        }
    return None


def _check_code_quality(files: List[str]) -> Dict | None:
    """Check for code quality tools."""
    quality_files = ['.eslintrc', '.prettierrc', 'pylint', '.flake8', 'tslint.json', '.editorconfig']
    has_quality = any(any(qf in f.lower() for qf in quality_files) for f in files)
    
    if not has_quality:
        return {
            'severity': 'low',
            'check': 'No Linting Config',
            'message': 'No code quality or linting configuration detected',
            'suggestion': 'Add ESLint, Prettier, Pylint, or similar tools to maintain code consistency'
        }
    return None


def _get_passed_checks(files: List[str]) -> List[Dict]:
    """Identify what the repository is doing well."""
    passed = []
    
    # Check README
    if any(f.lower().startswith('readme') for f in files):
        passed.append({
            'check': 'README Present',
            'message': 'Repository includes documentation for users and contributors'
        })
    
    # Check tests
    test_patterns = ['test', 'spec', '__tests__']
    if any(any(pattern in f.lower() for pattern in test_patterns) for f in files):
        passed.append({
            'check': 'Tests Included',
            'message': 'Test suite detected, ensuring code reliability'
        })
    
    # Check .gitignore
    if '.gitignore' in files:
        passed.append({
            'check': '.gitignore Present',
            'message': 'Properly configured to exclude unnecessary files'
        })
    
    # Check CI/CD
    ci_patterns = ['.github/workflows', '.gitlab-ci', 'jenkinsfile']
    if any(any(pattern in f.lower() for pattern in ci_patterns) for f in files):
        passed.append({
            'check': 'CI/CD Configured',
            'message': 'Automated testing and deployment pipeline in place'
        })
    
    # Check license
    if any(f.lower().startswith('license') for f in files):
        passed.append({
            'check': 'License Included',
            'message': 'Clear licensing terms for project usage'
        })
    
    # Check dependencies
    lock_files = ['package-lock.json', 'yarn.lock', 'poetry.lock', 'pipfile.lock']
    if any(f.lower() in lock_files for f in files):
        passed.append({
            'check': 'Lock File Present',
            'message': 'Dependencies locked for reproducible builds'
        })
    
    # Check security
    if '.env' not in files:
        passed.append({
            'check': 'No Exposed Secrets',
            'message': 'Environment files properly excluded from version control'
        })
    
    return passed


def analyze_pr_guardian(repo_data: dict) -> dict:
    """
    Intelligent PR readiness and health analysis using heuristics.
    NO AI APIs - pure rule-based intelligence.
    """
    files = repo_data.get('files', [])
    name = repo_data.get('name', 'Unknown')
    open_issues = repo_data.get('open_issues', 0)
    
    # Run all checks
    checks = [
        _check_readme,
        _check_tests,
        _check_gitignore,
        _check_env_exposure,
        _check_license,
        _check_ci_cd,
        _check_dependencies,
        _check_documentation,
        _check_code_quality
    ]
    
    issues = []
    for check_func in checks:
        result = check_func(files)
        if result:
            issues.append(result)
    
    # Get passed checks
    passed = _get_passed_checks(files)
    
    # Calculate score
    score, verdict, color = _calculate_health_score(issues)
    
    # Add open issues warning if significant
    if open_issues > 10:
        issues.append({
            'severity': 'medium',
            'check': 'High Issue Count',
            'message': f'{open_issues} open issues in repository',
            'suggestion': 'Review and triage open issues, close resolved ones, and prioritize critical bugs'
        })
    
    return {
        'score': score,
        'verdict': verdict,
        'verdictColor': color,
        'issues': issues,
        'passed': passed,
        'totalChecks': len(issues) + len(passed),
        'issueCount': len(issues),
        'passedCount': len(passed),
        'repoName': name,
        'openIssues': open_issues
    }

# Made with Bob
