"""
Repo Fixer Module
Generates actionable fixes for repository issues.
"""

from typing import Dict, Any, List


def generate_fixes(
    repo_data: Dict[str, Any],
    code_context: Dict[str, Any],
    pr_guardian: Dict[str, Any],
    debt_radar: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate actionable fixes for repository issues.
    
    Args:
        repo_data: Repository metadata
        code_context: Code context analysis
        pr_guardian: PR Guardian analysis
        debt_radar: Debt Radar analysis
    
    Returns:
        List of fix recommendations with code/steps
    """
    fixes = []
    
    # Extract data
    pr_issues = pr_guardian.get('issues', [])
    pr_passed = pr_guardian.get('passed', [])
    debt_issues = debt_radar.get('issues', [])
    tech_stack = code_context.get('techStack', [])
    language = repo_data.get('language', 'Unknown')
    
    # Check what's missing
    has_tests = any('test' in check.get('check', '').lower() for check in pr_passed)
    has_ci = any('ci' in check.get('check', '').lower() for check in pr_passed)
    has_linting = any('lint' in check.get('check', '').lower() for check in pr_passed)
    
    # Fix 1: Add Testing Setup
    if not has_tests:
        if "react" in " ".join(tech_stack).lower() or "javascript" in language.lower():
            fixes.append({
                'title': 'Add Testing Framework',
                'priority': 'high',
                'impact': 'Prevents bugs and ensures code quality',
                'steps': [
                    'Install Jest and React Testing Library',
                    'Create test configuration file',
                    'Write unit tests for components',
                    'Add test script to package.json'
                ],
                'code': """// package.json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0"
  }
}

// Example test file: App.test.js
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders app component', () => {
  render(<App />);
  expect(screen.getByText(/welcome/i)).toBeInTheDocument();
});"""
            })
        elif language.lower() == "python":
            fixes.append({
                'title': 'Add Testing Framework',
                'priority': 'high',
                'impact': 'Prevents bugs and ensures code quality',
                'steps': [
                    'Install pytest',
                    'Create tests directory',
                    'Write unit tests',
                    'Add test command to CI'
                ],
                'code': """# requirements-dev.txt
pytest==7.4.0
pytest-cov==4.1.0

# tests/test_app.py
import pytest

def test_example():
    assert 1 + 1 == 2

# Run tests
# pytest tests/ --cov=app"""
            })
    
    # Fix 2: Add CI/CD Pipeline
    if not has_ci:
        if "github" in repo_data.get('full_name', '').lower() or True:
            fixes.append({
                'title': 'Add GitHub Actions CI/CD',
                'priority': 'high',
                'impact': 'Automates testing and deployment',
                'steps': [
                    'Create .github/workflows directory',
                    'Add CI workflow file',
                    'Configure test and build steps',
                    'Add deployment if needed'
                ],
                'code': """# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Build
      run: npm run build"""
            })
    
    # Fix 3: Add Linting
    if not has_linting:
        if "javascript" in language.lower() or "typescript" in language.lower():
            fixes.append({
                'title': 'Add ESLint Configuration',
                'priority': 'medium',
                'impact': 'Enforces code style and catches errors',
                'steps': [
                    'Install ESLint',
                    'Create .eslintrc.json',
                    'Add lint script',
                    'Run linter on save'
                ],
                'code': """// .eslintrc.json
{
  "extends": ["eslint:recommended", "plugin:react/recommended"],
  "env": {
    "browser": true,
    "es2021": true,
    "node": true
  },
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "rules": {
    "no-unused-vars": "warn",
    "no-console": "warn"
  }
}

// package.json
{
  "scripts": {
    "lint": "eslint src/**/*.{js,jsx}",
    "lint:fix": "eslint src/**/*.{js,jsx} --fix"
  }
}"""
            })
        elif language.lower() == "python":
            fixes.append({
                'title': 'Add Python Linting',
                'priority': 'medium',
                'impact': 'Enforces PEP 8 and catches errors',
                'steps': [
                    'Install flake8 and black',
                    'Create .flake8 config',
                    'Add pre-commit hooks',
                    'Format code automatically'
                ],
                'code': """# requirements-dev.txt
flake8==6.0.0
black==23.0.0

# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503

# Format code
# black .
# flake8 ."""
            })
    
    # Fix 4: Address Critical Issues
    critical_issues = [i for i in pr_issues + debt_issues if i.get('severity') == 'critical']
    if critical_issues:
        for issue in critical_issues[:2]:
            fixes.append({
                'title': f"Fix: {issue.get('check') or issue.get('type')}",
                'priority': 'critical',
                'impact': issue.get('message') or issue.get('detail'),
                'steps': [
                    'Review the issue details',
                    'Implement the suggested fix',
                    'Test the changes',
                    'Commit and push'
                ],
                'code': f"# Suggestion: {issue.get('suggestion', 'Address this issue immediately')}"
            })
    
    # Fix 5: Refactor Large Files
    large_file_issues = [i for i in debt_issues if 'large' in i.get('type', '').lower() or 'complex' in i.get('type', '').lower()]
    if large_file_issues:
        fixes.append({
            'title': 'Refactor Large/Complex Files',
            'priority': 'medium',
            'impact': 'Improves maintainability and readability',
            'steps': [
                'Identify large files (>300 lines)',
                'Break into smaller modules',
                'Extract reusable functions',
                'Add proper documentation'
            ],
            'code': """// Before: Large component
function LargeComponent() {
  // 500 lines of code...
}

// After: Split into smaller components
function MainComponent() {
  return (
    <>
      <Header />
      <Content />
      <Footer />
    </>
  );
}

function Header() { /* ... */ }
function Content() { /* ... */ }
function Footer() { /* ... */ }"""
        })
    
    # Fix 6: Add Documentation
    if not any('readme' in check.get('check', '').lower() for check in pr_passed):
        fixes.append({
            'title': 'Improve Documentation',
            'priority': 'low',
            'impact': 'Helps onboarding and collaboration',
            'steps': [
                'Create/update README.md',
                'Add inline code comments',
                'Document API endpoints',
                'Add usage examples'
            ],
            'code': """# README.md
# Project Name

## Overview
Brief description of the project

## Installation
```bash
npm install
```

## Usage
```bash
npm start
```

## API Documentation
- GET /api/users - Get all users
- POST /api/users - Create user"""
        })
    
    # Fix 7: Add Environment Configuration
    fixes.append({
        'title': 'Add Environment Configuration',
        'priority': 'medium',
        'impact': 'Separates config from code, improves security',
        'steps': [
            'Create .env.example file',
            'Add .env to .gitignore',
            'Use environment variables',
            'Document required variables'
        ],
        'code': """# .env.example
DATABASE_URL=postgresql://localhost/mydb
API_KEY=your_api_key_here
PORT=3000
NODE_ENV=development

# .gitignore
.env
.env.local

# Usage in code
const dbUrl = process.env.DATABASE_URL;
const apiKey = process.env.API_KEY;"""
    })
    
    # Return top 5 fixes
    return fixes[:5]


# Made with Bob