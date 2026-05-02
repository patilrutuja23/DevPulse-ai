"""
Test script to verify all API endpoints are working correctly.
Run this to ensure IBM Bob integration is functioning.
"""

import requests
import json
import sys
import io

# Fix Windows console encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = 'http://127.0.0.1:5000'

def test_health():
    """Test health endpoint"""
    print('\n🔍 Testing /api/health...')
    try:
        resp = requests.get(f'{API_BASE}/api/health', timeout=5)
        data = resp.json()
        print(f'   Status: {resp.status_code}')
        print(f'   Response: {json.dumps(data, indent=2)}')
        
        if data.get('status') == 'ok':
            print('   ✅ Health check passed')
            if data.get('ibm_bob'):
                print('   ✅ IBM Bob configured')
            else:
                print('   ⚠️  IBM Bob NOT configured (set WATSONX_API_KEY and WATSONX_PROJECT_ID)')
            if data.get('github_token'):
                print('   ✅ GitHub token configured')
            else:
                print('   ⚠️  GitHub token NOT configured (set GITHUB_TOKEN)')
            return True
        return False
    except Exception as e:
        print(f'   ❌ Error: {e}')
        return False

def test_load_repo():
    """Test load-repo endpoint"""
    print('\n🔍 Testing /load-repo...')
    try:
        payload = {'repo_url': 'https://github.com/torvalds/linux'}
        resp = requests.post(
            f'{API_BASE}/load-repo',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        data = resp.json()
        print(f'   Status: {resp.status_code}')
        
        if resp.status_code == 200 and data.get('success'):
            repo_data = data.get('data', {})
            print(f'   ✅ Repository loaded: {repo_data.get("full_name")}')
            print(f'   Files found: {len(repo_data.get("files", []))}')
            return repo_data
        else:
            print(f'   ❌ Error: {data.get("error", "Unknown error")}')
            return None
    except Exception as e:
        print(f'   ❌ Error: {e}')
        return None

def test_code_context(repo_url):
    """Test code-context endpoint"""
    print('\n🔍 Testing /code-context...')
    try:
        payload = {'repo_url': repo_url}
        resp = requests.post(
            f'{API_BASE}/code-context',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        data = resp.json()
        print(f'   Status: {resp.status_code}')
        
        if resp.status_code == 200 and data.get('success'):
            result = data.get('data', {})
            print(f'   ✅ Code Context analysis complete')
            print(f'   Architecture: {result.get("architecture")}')
            print(f'   Tech Stack: {", ".join(result.get("techStack", [])[:5])}')
            print(f'   Modules detected: {len(result.get("modules", []))}')
            return True
        else:
            print(f'   ❌ Error: {data.get("error", "Unknown error")}')
            return False
    except Exception as e:
        print(f'   ❌ Error: {e}')
        return False

def test_pr_review(repo_url):
    """Test pr-review endpoint"""
    print('\n🔍 Testing /pr-review...')
    try:
        payload = {'repo_url': repo_url}
        resp = requests.post(
            f'{API_BASE}/pr-review',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        data = resp.json()
        print(f'   Status: {resp.status_code}')
        
        if resp.status_code == 200 and data.get('success'):
            result = data.get('data', {})
            print(f'   ✅ PR Guardian analysis complete')
            print(f'   Health Score: {result.get("score")}/100')
            print(f'   Verdict: {result.get("verdict")}')
            print(f'   Issues found: {result.get("issueCount", 0)}')
            print(f'   Checks passed: {result.get("passedCount", 0)}')
            return True
        else:
            print(f'   ❌ Error: {data.get("error", "Unknown error")}')
            return False
    except Exception as e:
        print(f'   ❌ Error: {e}')
        return False

def test_incident():
    """Test incident endpoint"""
    print('\n🔍 Testing /incident...')
    try:
        payload = {
            'error_message': 'TypeError: Cannot read property "length" of undefined',
            'code_snippet': '''
function processArray(arr) {
    for (let i = 0; i < arr.length; i++) {
        console.log(arr[i]);
    }
}
processArray();
'''
        }
        resp = requests.post(
            f'{API_BASE}/incident',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        data = resp.json()
        print(f'   Status: {resp.status_code}')
        
        if resp.status_code == 200 and data.get('success'):
            result = data.get('data', {})
            print(f'   ✅ Incident analysis complete')
            print(f'   Root Cause: {result.get("rootCause", "")[:80]}...')
            print(f'   Error Type: {result.get("errorType")}')
            print(f'   Severity: {result.get("severity")}')
            return True
        else:
            print(f'   ❌ Error: {data.get("error", "Unknown error")}')
            return False
    except Exception as e:
        print(f'   ❌ Error: {e}')
        return False

def test_debt(repo_url):
    """Test debt endpoint"""
    print('\n🔍 Testing /debt...')
    try:
        payload = {'repo_url': repo_url}
        resp = requests.post(
            f'{API_BASE}/debt',
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        data = resp.json()
        print(f'   Status: {resp.status_code}')
        
        if resp.status_code == 200 and data.get('success'):
            result = data.get('data', {})
            print(f'   ✅ Debt Radar analysis complete')
            print(f'   Debt Score: {result.get("debtScore")}/100')
            print(f'   Debt Level: {result.get("debtLevel")}')
            print(f'   Total Issues: {result.get("totalIssues", 0)}')
            return True
        else:
            print(f'   ❌ Error: {data.get("error", "Unknown error")}')
            return False
    except Exception as e:
        print(f'   ❌ Error: {e}')
        return False

def main():
    print('=' * 60)
    print('DevPulse AI - API Test Suite')
    print('=' * 60)
    
    # Test health first
    if not test_health():
        print('\n❌ Health check failed. Make sure the Flask server is running.')
        print('   Run: python backend/app.py')
        sys.exit(1)
    
    # Use a small test repo
    test_repo = 'https://github.com/octocat/Hello-World'
    
    # Test load-repo
    repo_data = test_load_repo()
    if not repo_data:
        print('\n⚠️  Could not load repository. Skipping module tests.')
        sys.exit(1)
    
    # Test all modules
    results = {
        'Code Context': test_code_context(test_repo),
        'PR Guardian': test_pr_review(test_repo),
        'Incident Whisperer': test_incident(),
        'Debt Radar': test_debt(test_repo),
    }
    
    # Summary
    print('\n' + '=' * 60)
    print('Test Summary')
    print('=' * 60)
    for module, passed in results.items():
        status = '✅ PASSED' if passed else '❌ FAILED'
        print(f'{module:20} {status}')
    
    all_passed = all(results.values())
    print('=' * 60)
    if all_passed:
        print('✅ All API endpoints are working correctly!')
    else:
        print('⚠️  Some tests failed. Check the output above for details.')
    
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()

# Made with Bob
