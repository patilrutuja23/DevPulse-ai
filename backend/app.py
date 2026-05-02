"""
DevPulse AI - Flask API Server
6 endpoints: /load-repo, /code-context, /pr-review, /incident, /debt, /repo-summary
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from repo_ingestion import load_repo
from modules.codecontext import analyze_code_context
from modules.pr_guardian import analyze_pr_guardian
from modules.incident_whisperer import analyze_incident
from modules.debt_radar import analyze_debt_radar
from modules.repo_brain import analyze_repo_brain
from modules.readme_generator import generate_readme
from modules.repo_fixer import generate_fixes

load_dotenv()

app = Flask(__name__)
CORS(app)

# Debug: Print token status at startup
print("=" * 60)
print("DevPulse AI - Environment Check")
print("=" * 60)
github_token_check = os.getenv('GITHUB_TOKEN')
print(f"ENV TOKEN: {'✓ Present' if github_token_check else '✗ Missing'}")
if github_token_check:
    token_preview = github_token_check[:10] + "..." if len(github_token_check) > 10 else "too short"
    print(f"Token Preview: {token_preview}")
print("=" * 60)

# Initialise IBM Bob at startup so we fail fast if credentials are missing
try:
    from bob_client import get_bob
    get_bob()
except EnvironmentError as _bob_err:
    print(f'⚠️  IBM Bob not configured: {_bob_err}')
    print('   Set WATSONX_API_KEY and WATSONX_PROJECT_ID in .env to enable AI features.')


def err(msg, status=400):
    return jsonify({'error': msg}), status


# ── Health ────────────────────────────────────────────────────────────────────

@app.route('/api/health')
def health():
    bob_ready = bool(os.getenv('WATSONX_API_KEY') and os.getenv('WATSONX_PROJECT_ID'))
    github_token = os.getenv('GITHUB_TOKEN')
    return jsonify({
        'status': 'ok',
        'ibm_bob': bob_ready,
        'github_token': bool(github_token)
    })


# ── 1. Load Repository ────────────────────────────────────────────────────────

@app.route('/load-repo', methods=['POST'])
def route_load_repo():
    """
    POST /load-repo
    Body: { "repo_url": "https://github.com/owner/repo" }
    Returns: repo metadata + file list
    """
    data = request.get_json(silent=True) or {}
    repo_url = (data.get('repo_url') or '').strip()

    if not repo_url:
        return err('repo_url is required')

    github_token = os.getenv('GITHUB_TOKEN')
    print(f"🔑 Using GitHub Token: {'✓ Present' if github_token else '✗ Missing'}")
    result = load_repo(repo_url, github_token)

    if 'error' in result:
        return err(result['error'], 422)

    return jsonify({'success': True, 'data': result})


# ── 2. Code Context ───────────────────────────────────────────────────────────

@app.route('/code-context', methods=['POST'])
def route_code_context():
    """
    POST /code-context
    Body: { "repo_url": "https://github.com/owner/repo" }
    Returns: architecture, techStack, modules
    """
    data = request.get_json(silent=True) or {}
    repo_url = (data.get('repo_url') or '').strip()

    if not repo_url:
        return err('repo_url is required')

    github_token = os.getenv('GITHUB_TOKEN')
    print(f"🔑 Using GitHub Token: {'✓ Present' if github_token else '✗ Missing'}")
    repo_data = load_repo(repo_url, github_token)
    if 'error' in repo_data:
        return err(repo_data['error'], 422)

    result = analyze_code_context(repo_data)
    return jsonify({'success': True, 'data': result})


# ── 3. PR Guardian ────────────────────────────────────────────────────────────

@app.route('/pr-review', methods=['POST'])
def route_pr_review():
    """
    POST /pr-review
    Body: { "repo_url": "https://github.com/owner/repo" }
    Returns: health score, issues list, passed checks
    """
    data = request.get_json(silent=True) or {}
    repo_url = (data.get('repo_url') or '').strip()

    if not repo_url:
        return err('repo_url is required')

    github_token = os.getenv('GITHUB_TOKEN')
    print(f"🔑 Using GitHub Token: {'✓ Present' if github_token else '✗ Missing'}")
    repo_data = load_repo(repo_url, github_token)
    if 'error' in repo_data:
        return err(repo_data['error'], 422)

    result = analyze_pr_guardian(repo_data)
    return jsonify({'success': True, 'data': result})


# ── 4. Incident Whisperer ─────────────────────────────────────────────────────

@app.route('/incident', methods=['POST'])
def route_incident():
    """
    POST /incident
    Body: { "error_message": "...", "code_snippet": "..." }
    Returns: rootCause, explanation, fix, updatedCode, reproductionSteps
    """
    data = request.get_json(silent=True) or {}
    error_message = (data.get('error_message') or '').strip()
    code_snippet = (data.get('code_snippet') or '').strip()

    if not error_message:
        return err('error_message is required')
    if not code_snippet:
        return err('code_snippet is required')

    result = analyze_incident(error_message, code_snippet)
    return jsonify({'success': True, 'data': result})


# ── 5. Debt Radar ─────────────────────────────────────────────────────────────

@app.route('/debt', methods=['POST'])
def route_debt():
    """
    POST /debt
    Body: { "repo_url": "https://github.com/owner/repo" }
    Returns: debtScore, debtLevel, issues, suggestions
    """
    data = request.get_json(silent=True) or {}
    repo_url = (data.get('repo_url') or '').strip()

    if not repo_url:
        return err('repo_url is required')

    github_token = os.getenv('GITHUB_TOKEN')
    print(f"🔑 Using GitHub Token: {'✓ Present' if github_token else '✗ Missing'}")
    repo_data = load_repo(repo_url, github_token)
    if 'error' in repo_data:
        return err(repo_data['error'], 422)

    result = analyze_debt_radar(repo_data, github_token)
    return jsonify({'success': True, 'data': result})


# ── 6. Repo Summary (Unified Intelligence) ────────────────────────────────────

@app.route('/repo-summary', methods=['POST'])
def route_repo_summary():
    """
    POST /repo-summary
    Body: { "repo_url": "https://github.com/owner/repo" }
    Returns: Unified intelligence assessment combining all modules
    """
    data = request.get_json(silent=True) or {}
    repo_url = (data.get('repo_url') or '').strip()

    if not repo_url:
        return err('repo_url is required')

    github_token = os.getenv('GITHUB_TOKEN')
    print(f"🧠 Running unified intelligence analysis for: {repo_url}")
    
    # Step 1: Load repository
    repo_data = load_repo(repo_url, github_token)
    if 'error' in repo_data:
        return err(repo_data['error'], 422)

    # Step 2: Run all analysis modules
    print("  → Analyzing code context...")
    code_context = analyze_code_context(repo_data)
    
    print("  → Analyzing PR health...")
    pr_guardian = analyze_pr_guardian(repo_data)
    
    print("  → Analyzing technical debt...")
    debt_radar = analyze_debt_radar(repo_data, github_token)
    
    # Step 3: Run unified brain analysis
    print("  → Generating unified intelligence...")
    brain_summary = analyze_repo_brain(code_context, pr_guardian, debt_radar)
    
    print(f"✓ Analysis complete: {brain_summary['verdict']} ({brain_summary['overallScore']}/100)")
    
    return jsonify({
        'success': True,
        'data': {
            'summary': brain_summary,
            'details': {
                'codeContext': code_context,
                'prGuardian': pr_guardian,
                'debtRadar': debt_radar
            }
        }
    })


# ── 7. Generate README ────────────────────────────────────────────────────────

@app.route('/generate-readme', methods=['POST'])
def route_generate_readme():
    """
    POST /generate-readme
    Body: { "repo_url": "https://github.com/owner/repo" }
    Returns: Generated README content
    """
    data = request.get_json(silent=True) or {}
    repo_url = (data.get('repo_url') or '').strip()

    if not repo_url:
        return err('repo_url is required')

    github_token = os.getenv('GITHUB_TOKEN')
    print(f"📄 Generating README for: {repo_url}")
    
    # Load repository
    repo_data = load_repo(repo_url, github_token)
    if 'error' in repo_data:
        return err(repo_data['error'], 422)

    # Run analysis modules
    code_context = analyze_code_context(repo_data)
    pr_guardian = analyze_pr_guardian(repo_data)
    debt_radar = analyze_debt_radar(repo_data, github_token)
    
    # Generate README
    readme_content = generate_readme(repo_data, code_context, pr_guardian, debt_radar)
    
    print(f"✓ README generated ({len(readme_content)} characters)")
    
    return jsonify({
        'success': True,
        'data': {
            'content': readme_content,
            'length': len(readme_content)
        }
    })


# ── 8. Fix My Repo ────────────────────────────────────────────────────────────

@app.route('/fix-repo', methods=['POST'])
def route_fix_repo():
    """
    POST /fix-repo
    Body: { "repo_url": "https://github.com/owner/repo" }
    Returns: List of actionable fixes
    """
    data = request.get_json(silent=True) or {}
    repo_url = (data.get('repo_url') or '').strip()

    if not repo_url:
        return err('repo_url is required')

    github_token = os.getenv('GITHUB_TOKEN')
    print(f"🛠 Generating fixes for: {repo_url}")
    
    # Load repository
    repo_data = load_repo(repo_url, github_token)
    if 'error' in repo_data:
        return err(repo_data['error'], 422)

    # Run analysis modules
    code_context = analyze_code_context(repo_data)
    pr_guardian = analyze_pr_guardian(repo_data)
    debt_radar = analyze_debt_radar(repo_data, github_token)
    
    # Generate fixes
    fixes = generate_fixes(repo_data, code_context, pr_guardian, debt_radar)
    
    print(f"✓ Generated {len(fixes)} fixes")
    
    return jsonify({
        'success': True,
        'data': {
            'fixes': fixes,
            'totalFixes': len(fixes)
        }
    })


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(_):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': str(e)}), 500


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    print(f'DevPulse AI running on http://127.0.0.1:{port}')
    app.run(host='127.0.0.1', port=port, debug=debug)
