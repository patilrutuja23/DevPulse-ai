# Sample API Responses - DevPulse AI

## 1. Repo Summary (Unified Intelligence)

### Request:
```bash
POST http://127.0.0.1:5000/repo-summary
Content-Type: application/json

{
  "repo_url": "https://github.com/facebook/react"
}
```

### Response:
```json
{
  "success": true,
  "data": {
    "summary": {
      "overallScore": 88,
      "verdict": "Good",
      "summary": "This frontend SPA project demonstrates solid engineering with room for improvement. Found 3 strengths with 2 areas for improvement. Focus on addressing high-priority issues to improve quality.",
      "confidence": 92,
      "riskFactors": [
        {
          "factor": "No CI/CD",
          "impact": "Manual testing and deployment increases error risk and slows down releases",
          "severity": "high",
          "source": "PR Guardian"
        },
        {
          "factor": "Low Test Coverage",
          "impact": "Only 15 test files for 120 source files (ratio: 1:8)",
          "severity": "high",
          "source": "Debt Radar"
        }
      ],
      "strengths": [
        {
          "strength": "README Present",
          "detail": "Repository includes documentation for users and contributors",
          "source": "PR Guardian"
        },
        {
          "strength": "Modern Tech Stack",
          "detail": "Leverages 8 technologies including React, TypeScript, Webpack",
          "source": "Code Context"
        },
        {
          "strength": "High Code Quality",
          "detail": "Repository health score of 85/100 indicates strong practices",
          "source": "PR Guardian"
        }
      ],
      "topFixes": [
        {
          "priority": 2,
          "action": "Improve: No CI/CD",
          "reason": "Manual testing and deployment increases error risk and slows down releases",
          "suggestion": "Set up GitHub Actions, GitLab CI, or Jenkins for automated testing and deployment",
          "impact": "High"
        },
        {
          "priority": 2,
          "action": "Improve: Low Test Coverage",
          "reason": "Only 15 test files for 120 source files (ratio: 1:8)",
          "suggestion": "Increase test coverage by adding more test files. Target ratio of at least 1:5",
          "impact": "High"
        },
        {
          "priority": 3,
          "action": "⚠️ HIGH PRIORITY: Resolve 2 high-severity technical debt items",
          "reason": "Reduces technical debt and improves maintainability",
          "suggestion": "⚠️ HIGH PRIORITY: Resolve 2 high-severity technical debt items",
          "impact": "Medium"
        }
      ],
      "metrics": {
        "prHealthScore": 85,
        "debtScore": 35,
        "criticalIssues": 0,
        "highIssues": 2,
        "totalFiles": 120,
        "hasTests": true,
        "hasCI": false,
        "hasDocs": true
      },
      "projectInfo": {
        "name": "react",
        "architecture": "Frontend SPA",
        "language": "JavaScript",
        "techStack": ["JavaScript", "React", "TypeScript", "Webpack", "Jest"]
      }
    },
    "details": {
      "codeContext": {
        "architecture": "Frontend SPA",
        "architectureDescription": "Single-page application focused on client-side rendering and user interface, likely consuming external APIs.",
        "techStack": ["JavaScript", "React", "TypeScript", "Webpack", "Jest", "ESLint", "Prettier"],
        "modules": [
          {
            "name": "src/",
            "purpose": "Source code directory"
          },
          {
            "name": "packages/",
            "purpose": "Package modules"
          }
        ],
        "insights": "Large-scale project with 120 files, suggesting enterprise-level complexity. Rich technology stack with 7 technologies, indicating a mature and feature-rich application. Test coverage detected, indicating commitment to code quality.",
        "projectMaturity": "Mature",
        "totalFiles": 120,
        "repoName": "react",
        "language": "JavaScript"
      },
      "prGuardian": {
        "score": 85,
        "verdict": "Good",
        "verdictColor": "green",
        "issues": [
          {
            "severity": "medium",
            "check": "No CI/CD",
            "message": "No continuous integration configuration detected",
            "suggestion": "Set up GitHub Actions, GitLab CI, or Jenkins for automated testing and deployment",
            "impact": "Manual testing and deployment increases error risk and slows down releases"
          }
        ],
        "passed": [
          {
            "check": "README Present",
            "message": "Repository includes documentation for users and contributors"
          },
          {
            "check": "Tests Included",
            "message": "Test suite detected, ensuring code reliability"
          },
          {
            "check": ".gitignore Present",
            "message": "Properly configured to exclude unnecessary files"
          },
          {
            "check": "License Included",
            "message": "Clear licensing terms for project usage"
          },
          {
            "check": "No Exposed Secrets",
            "message": "Environment files properly excluded from version control"
          }
        ],
        "totalChecks": 6,
        "issueCount": 1,
        "passedCount": 5
      },
      "debtRadar": {
        "debtScore": 35,
        "debtLevel": "Medium",
        "totalIssues": 3,
        "severityCounts": {
          "critical": 0,
          "high": 2,
          "medium": 1,
          "low": 0
        },
        "issues": [
          {
            "type": "Low Test Coverage",
            "severity": "high",
            "file": "N/A",
            "detail": "Only 15 test files for 120 source files (ratio: 1:8)",
            "suggestion": "Increase test coverage by adding more test files. Target ratio of at least 1:5",
            "businessImpact": "Increased bug risk, slower feature development, costly regressions",
            "priorityLevel": "High"
          },
          {
            "type": "No CI/CD Pipeline",
            "severity": "high",
            "file": "N/A",
            "detail": "No continuous integration or deployment configuration detected",
            "suggestion": "Set up GitHub Actions, GitLab CI, or Jenkins for automated testing and deployment",
            "businessImpact": "Manual deployments increase errors, slower releases, inconsistent quality",
            "priorityLevel": "High"
          },
          {
            "type": "No Code Quality Tools",
            "severity": "medium",
            "file": "N/A",
            "detail": "No linting or formatting configuration detected",
            "suggestion": "Add ESLint, Prettier, Pylint, or similar tools to maintain code consistency",
            "businessImpact": "Inconsistent code style, harder code reviews, more bugs slip through",
            "priorityLevel": "Medium"
          }
        ],
        "suggestions": [
          "⚠️ HIGH PRIORITY: Resolve 2 high-severity technical debt items",
          "Implement comprehensive test suite to ensure code reliability",
          "Set up automated CI/CD pipeline for consistent deployments"
        ]
      }
    }
  }
}
```

---

## 2. Code Context

### Response:
```json
{
  "success": true,
  "data": {
    "architecture": "REST API / MVC",
    "architectureDescription": "Model-View-Controller backend service exposing RESTful APIs for client consumption.",
    "techStack": ["Python", "Flask", "Docker", "Pytest", "GitHub Actions"],
    "modules": [
      {
        "name": "api/",
        "purpose": "API endpoints and route handlers"
      },
      {
        "name": "models/",
        "purpose": "Data models and database schemas"
      },
      {
        "name": "tests/",
        "purpose": "Test suites and test cases"
      }
    ],
    "insights": "Well-organized project with 45 files, indicating moderate complexity. Balanced tech stack leveraging 5 core technologies for optimal development. Test coverage detected, indicating commitment to code quality and reliability.",
    "projectMaturity": "Growing",
    "totalFiles": 45,
    "repoName": "my-api",
    "language": "Python",
    "description": "RESTful API for data management"
  }
}
```

---

## 3. PR Guardian

### Response:
```json
{
  "success": true,
  "data": {
    "score": 72,
    "verdict": "Needs Improvement",
    "verdictColor": "yellow",
    "issues": [
      {
        "severity": "high",
        "check": "No Tests",
        "message": "No test files detected in repository",
        "suggestion": "Add unit tests using Jest, Pytest, or appropriate testing framework",
        "impact": "Significantly increases risk of production bugs and makes refactoring dangerous"
      },
      {
        "severity": "medium",
        "check": "No CI/CD",
        "message": "No continuous integration configuration detected",
        "suggestion": "Set up GitHub Actions, GitLab CI, or Jenkins for automated testing and deployment",
        "impact": "Manual testing and deployment increases error risk and slows down releases"
      }
    ],
    "passed": [
      {
        "check": "README Present",
        "message": "Repository includes documentation for users and contributors"
      },
      {
        "check": ".gitignore Present",
        "message": "Properly configured to exclude unnecessary files"
      }
    ],
    "totalChecks": 4,
    "issueCount": 2,
    "passedCount": 2,
    "repoName": "my-api",
    "openIssues": 5
  }
}
```

---

## 4. Incident Whisperer

### Response (Specific Error):
```json
{
  "success": true,
  "data": {
    "rootCause": "Variable or property 'userData' is accessed before being defined or initialized",
    "explanation": "The error occurs because 'userData' is being used in the code but hasn't been declared, initialized, or is out of scope. This commonly happens with typos, missing imports, or accessing properties on null/undefined objects.",
    "fix": "1. Check if 'userData' is spelled correctly\n2. Ensure 'userData' is declared before use (let, const, var)\n3. If it's an import, verify the import statement\n4. Add null/undefined checks before accessing properties",
    "updatedCode": "if (userData) {\n  console.log(userData.name);\n}",
    "reproductionSteps": [
      "Run the code without declaring 'userData'",
      "Attempt to access 'userData' in the current scope",
      "Observe the undefined error"
    ],
    "errorType": "JavaScript Runtime Error",
    "severity": "high",
    "errorMessage": "TypeError: Cannot read property 'name' of undefined",
    "possibleCauses": [
      "Review error message for specific cause"
    ],
    "debuggingChecklist": [
      "✓ Check error message",
      "✓ Review code logic"
    ]
  }
}
```

### Response (Vague Error):
```json
{
  "success": true,
  "data": {
    "rootCause": "Insufficient error information provided",
    "explanation": "The error description is too vague to pinpoint the exact issue. Common causes include silent failures, missing error handling, or incorrect assumptions about code behavior.",
    "fix": "1. Add console.log() or print() statements to trace execution\n2. Check browser console or terminal for actual error messages\n3. Verify inputs and outputs at each step\n4. Use debugger breakpoints to inspect state\n5. Check network tab for failed API calls",
    "updatedCode": "// Add debugging to identify the issue\nconsole.log('Starting execution...');\ntry {\n  myFunction();\n  console.log('Execution completed successfully');\n} catch (error) {\n  console.error('Error caught:', error);\n  console.error('Stack trace:', error.stack);\n}",
    "reproductionSteps": [
      "Add logging statements throughout the code",
      "Run the code and check console output",
      "Identify where execution stops or behaves unexpectedly",
      "Look for actual error messages in console"
    ],
    "possibleCauses": [
      "Silent exception being caught and ignored",
      "Asynchronous operation not completing",
      "Missing return statement or incorrect logic",
      "Network request failing without error handling",
      "Incorrect variable scope or timing issue"
    ],
    "debuggingChecklist": [
      "✓ Check browser/terminal console for errors",
      "✓ Verify all variables are defined and have expected values",
      "✓ Confirm functions are being called",
      "✓ Check network tab for failed requests",
      "✓ Verify async operations are properly awaited",
      "✓ Look for typos in variable/function names"
    ],
    "errorType": "Vague Error Description",
    "severity": "medium",
    "errorMessage": "not working"
  }
}
```

---

## 5. Debt Radar

### Response:
```json
{
  "success": true,
  "data": {
    "debtScore": 45,
    "debtLevel": "Medium",
    "totalIssues": 6,
    "severityCounts": {
      "critical": 0,
      "high": 2,
      "medium": 3,
      "low": 1
    },
    "issues": [
      {
        "type": "No Test Coverage",
        "severity": "critical",
        "file": "N/A",
        "detail": "No test files detected in repository, indicating zero test coverage",
        "suggestion": "Implement unit tests using Jest, Pytest, or appropriate framework. Aim for 80%+ coverage",
        "businessImpact": "High risk of production bugs, expensive hotfixes, customer dissatisfaction",
        "priorityLevel": "Critical"
      },
      {
        "type": "Missing README",
        "severity": "high",
        "file": "N/A",
        "detail": "No README file found, making it difficult for developers to understand the project",
        "suggestion": "Create README.md with project overview, setup instructions, and usage examples",
        "businessImpact": "Slow developer onboarding, reduced collaboration, poor project adoption",
        "priorityLevel": "High"
      },
      {
        "type": "No CI/CD Pipeline",
        "severity": "high",
        "file": "N/A",
        "detail": "No continuous integration or deployment configuration detected",
        "suggestion": "Set up GitHub Actions, GitLab CI, or Jenkins for automated testing and deployment",
        "businessImpact": "Manual deployments increase errors, slower releases, inconsistent quality",
        "priorityLevel": "High"
      }
    ],
    "suggestions": [
      "🚨 URGENT: Address 0 critical security/quality issues immediately",
      "⚠️ HIGH PRIORITY: Resolve 2 high-severity technical debt items",
      "Implement comprehensive test suite to ensure code reliability",
      "Set up automated CI/CD pipeline for consistent deployments",
      "Improve documentation to enhance developer onboarding and maintenance"
    ],
    "repoName": "my-project",
    "filesAnalyzed": 45
  }
}
```

---

## Testing the API

### Using curl:
```bash
# Health check
curl http://127.0.0.1:5000/api/health

# Repo summary (unified intelligence)
curl -X POST http://127.0.0.1:5000/repo-summary \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/facebook/react"}'

# Code context
curl -X POST http://127.0.0.1:5000/code-context \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/facebook/react"}'

# PR Guardian
curl -X POST http://127.0.0.1:5000/pr-review \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/facebook/react"}'

# Debt Radar
curl -X POST http://127.0.0.1:5000/debt \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/facebook/react"}'

# Incident Whisperer
curl -X POST http://127.0.0.1:5000/incident \
  -H "Content-Type: application/json" \
  -d '{
    "error_message": "TypeError: Cannot read property name of undefined",
    "code_snippet": "console.log(user.name);"
  }'
```

### Using Python:
```python
import requests

API = "http://127.0.0.1:5000"

# Repo summary
response = requests.post(
    f"{API}/repo-summary",
    json={"repo_url": "https://github.com/facebook/react"}
)
data = response.json()
print(f"Overall Score: {data['data']['summary']['overallScore']}")
print(f"Verdict: {data['data']['summary']['verdict']}")
```

---

## Key Response Features

### 1. **Consistent Structure**
All responses follow the same pattern:
```json
{
  "success": true/false,
  "data": {...}
}
```

### 2. **Rich Context**
Every issue includes:
- Severity level
- Clear message
- Actionable suggestion
- Business impact (new!)
- Priority level (new!)

### 3. **Unified Intelligence**
The `/repo-summary` endpoint combines all modules into ONE intelligent assessment with:
- Overall score
- Verdict
- Confidence level
- Risk factors
- Strengths
- Prioritized fixes

### 4. **Business Language**
Not just technical details - explains WHY it matters to the business.

---

## Response Times

- `/repo-summary`: ~2-3 seconds (runs all modules)
- `/code-context`: ~0.5 seconds
- `/pr-review`: ~0.3 seconds
- `/debt`: ~1-2 seconds (fetches file sizes)
- `/incident`: ~0.1 seconds

All responses are **instant** compared to AI API calls (which take 5-10 seconds).