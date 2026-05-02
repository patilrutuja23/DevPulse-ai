"""
DevPulse AI - Flask API Server
5 endpoints: /load-repo, /code-context, /pr-review, /incident, /debt
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

load_dotenv()

app = Flask(__name__)
CORS(app)

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

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
    return jsonify({
        'status': 'ok',
        'ibm_bob': bob_ready,
        'github_token': bool(GITHUB_TOKEN)
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

    result = load_repo(repo_url, GITHUB_TOKEN)

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

    repo_data = load_repo(repo_url, GITHUB_TOKEN)
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

    repo_data = load_repo(repo_url, GITHUB_TOKEN)
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

    repo_data = load_repo(repo_url, GITHUB_TOKEN)
    if 'error' in repo_data:
        return err(repo_data['error'], 422)

    result = analyze_debt_radar(repo_data, GITHUB_TOKEN)
    return jsonify({'success': True, 'data': result})


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
