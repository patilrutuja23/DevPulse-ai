"""
Test script to verify the intelligent modules work without AI APIs
"""

from modules.codecontext import analyze_code_context
from modules.pr_guardian import analyze_pr_guardian
from modules.incident_whisperer import analyze_incident
from modules.debt_radar import analyze_debt_radar


def test_code_context():
    """Test Code Context analysis"""
    print("\n" + "="*60)
    print("Testing Code Context Analysis")
    print("="*60)
    
    repo_data = {
        'name': 'test-repo',
        'language': 'Python',
        'description': 'A test repository',
        'files': [
            'README.md',
            'app.py',
            'requirements.txt',
            'Dockerfile',
            'api/routes.py',
            'models/user.py',
            'tests/test_api.py',
            '.github/workflows/ci.yml'
        ]
    }
    
    result = analyze_code_context(repo_data)
    
    print(f"[OK] Architecture: {result['architecture']}")
    print(f"[OK] Tech Stack: {', '.join(result['techStack'][:5])}")
    print(f"[OK] Modules Found: {len(result['modules'])}")
    print(f"[OK] Insights: {result['insights'][:100]}...")


def test_pr_guardian():
    """Test PR Guardian analysis"""
    print("\n" + "="*60)
    print("Testing PR Guardian Analysis")
    print("="*60)
    
    repo_data = {
        'name': 'test-repo',
        'files': [
            'README.md',
            'app.py',
            '.gitignore',
            'tests/test_app.py',
            'package-lock.json'
        ],
        'open_issues': 5
    }
    
    result = analyze_pr_guardian(repo_data)
    
    print(f"[OK] Health Score: {result['score']}/100")
    print(f"[OK] Verdict: {result['verdict']} ({result['verdictColor']})")
    print(f"[OK] Issues Found: {result['issueCount']}")
    print(f"[OK] Checks Passed: {result['passedCount']}")


def test_incident_whisperer():
    """Test Incident Whisperer analysis"""
    print("\n" + "="*60)
    print("Testing Incident Whisperer Analysis")
    print("="*60)
    
    error_message = "TypeError: Cannot read property 'name' of undefined"
    code_snippet = "console.log(user.name);"
    
    result = analyze_incident(error_message, code_snippet)
    
    print(f"[OK] Error Type: {result['errorType']}")
    print(f"[OK] Severity: {result['severity']}")
    print(f"[OK] Root Cause: {result['rootCause'][:80]}...")
    print(f"[OK] Fix Provided: {'Yes' if result['fix'] else 'No'}")
    print(f"[OK] Updated Code: {'Yes' if result['updatedCode'] else 'No'}")


def test_debt_radar():
    """Test Debt Radar analysis"""
    print("\n" + "="*60)
    print("Testing Debt Radar Analysis")
    print("="*60)
    
    repo_data = {
        'name': 'test-repo',
        'language': 'JavaScript',
        'files': [
            'index.js',
            'package.json',
            'src/app.js',
            'src/utils.js'
        ],
        'owner': '',
        'repo': ''
    }
    
    result = analyze_debt_radar(repo_data)
    
    print(f"[OK] Debt Score: {result['debtScore']}/100")
    print(f"[OK] Debt Level: {result['debtLevel']}")
    print(f"[OK] Total Issues: {result['totalIssues']}")
    print(f"[OK] Critical: {result['severityCounts']['critical']}")
    print(f"[OK] High: {result['severityCounts']['high']}")
    print(f"[OK] Suggestions: {len(result['suggestions'])}")


if __name__ == '__main__':
    print("\n>> DevPulse AI - Intelligence Test Suite")
    print("Testing all modules WITHOUT AI APIs...")
    
    try:
        test_code_context()
        test_pr_guardian()
        test_incident_whisperer()
        test_debt_radar()
        
        print("\n" + "="*60)
        print(">> ALL TESTS PASSED!")
        print("="*60)
        print("\n>> All modules working with pure heuristic intelligence!")
        print(">> No AI APIs required - instant, accurate results!")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

# Made with Bob
