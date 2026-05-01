"""
DevPulse AI - Flask API Server
===============================

Main API server providing endpoints for all 4 AI modules:
1. CodeContext - Repository understanding
2. PR Guardian - Pull request review
3. Incident Whisperer - Bug analysis
4. Debt Radar - Technical debt detection
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import traceback

# Import modules
from bob_client import BobClient, create_bob_client
from modules.codecontext import analyze_code_context, analyze_specific_component
from modules.pr_guardian import analyze_pull_request, quick_pr_check
from modules.incident_whisperer import analyze_incident, quick_error_diagnosis
from modules.debt_radar import analyze_technical_debt, analyze_file_complexity

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

# Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JSON_SORT_KEYS'] = False

# Global client cache (in production, use Redis or similar)
client_cache = {}

# Global cache for Debt Radar scan results
debt_scan_cache = {}


def get_or_create_client(repo_url: str) -> BobClient:
    """
    Get cached client or create new one.
    
    Args:
        repo_url: GitHub repository URL
    
    Returns:
        BobClient instance
    """
    if repo_url not in client_cache:
        api_key = os.getenv("WATSONX_API_KEY")
        project_id = os.getenv("WATSONX_PROJECT_ID")
        github_token = os.getenv("GITHUB_TOKEN")
        
        if not api_key or not project_id:
            raise ValueError("WATSONX_API_KEY and WATSONX_PROJECT_ID must be set")
        
        client_cache[repo_url] = BobClient(api_key, project_id, repo_url, github_token)
    
    return client_cache[repo_url]


def handle_error(error: Exception, module: str = "API") -> tuple:
    """
    Handle errors and return appropriate response.
    
    Args:
        error: Exception that occurred
        module: Module name where error occurred
    
    Returns:
        Tuple of (response_dict, status_code)
    """
    error_trace = traceback.format_exc()
    print(f"Error in {module}: {str(error)}")
    print(error_trace)
    
    return jsonify({
        "error": str(error),
        "module": module,
        "success": False
    }), 500


# ============================================
# Health Check & Info Endpoints
# ============================================

@app.route('/')
def index():
    """Root endpoint with API information."""
    return jsonify({
        "name": "DevPulse AI API",
        "version": "1.0.0",
        "description": "Developer Intelligence Platform with 4 AI-powered modules",
        "modules": {
            "codecontext": "Repository understanding & architecture analysis",
            "pr_guardian": "Automated pull request review",
            "incident_whisperer": "Bug analysis & root cause detection",
            "debt_radar": "Technical debt identification"
        },
        "endpoints": {
            "health": "/api/health",
            "code_context": "/api/analyze/context",
            "pr_review": "/api/analyze/pr",
            "incident": "/api/analyze/incident",
            "tech_debt": "/api/analyze/debt"
        },
        "status": "operational"
    })


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "watsonx_configured": bool(os.getenv("WATSONX_API_KEY")),
        "github_configured": bool(os.getenv("GITHUB_TOKEN")),
        "modules_loaded": True
    })


# ============================================
# Module 1: CodeContext Endpoints
# ============================================

@app.route('/api/analyze/context', methods=['POST'])
def api_analyze_context():
    """
    Analyze repository architecture and code context.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo",
        "additional_context": "optional additional context"
    }
    """
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        additional_context = data.get('additional_context', '')
        
        if not repo_url:
            return jsonify({"error": "repo_url is required"}), 400
        
        # Get or create client
        client = get_or_create_client(repo_url)
        
        # Analyze
        result = analyze_code_context(client, additional_context)
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        return handle_error(e, "CodeContext")


@app.route('/api/analyze/context/component', methods=['POST'])
def api_analyze_component():
    """
    Analyze a specific component in detail.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo",
        "component_path": "src/app.py"
    }
    """
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        component_path = data.get('component_path')
        
        if not repo_url or not component_path:
            return jsonify({"error": "repo_url and component_path are required"}), 400
        
        client = get_or_create_client(repo_url)
        result = analyze_specific_component(client, component_path)
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        return handle_error(e, "CodeContext")

@app.route('/api/codecontext/analyze', methods=['POST'])
def api_codecontext_analyze():
    """
    Analyze repository using CodeContextEngine.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo"
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "project_name": "...",
            "purpose": "...",
            "tech_stack": [...],
            "architecture": "...",
            "modules": [...],
            "data_flow": "...",
            "entry_points": [...],
            "dependencies": [...],
            "complexity_score": 1-10
        }
    }
    """
    try:
        from modules.codecontext import CodeContextEngine
        
        data = request.get_json()
        repo_url = data.get('repo_url')
        
        if not repo_url:
            return jsonify({"error": "repo_url is required", "success": False}), 400
        
        # Get or create client
        client = get_or_create_client(repo_url)
        
        # Create engine and analyze
        engine = CodeContextEngine()
        result = engine.analyze_repo(client)
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        return handle_error(e, "CodeContextEngine")


@app.route('/api/codecontext/ask', methods=['POST'])
def api_codecontext_ask():
    """
    Ask a question about the codebase using CodeContextEngine.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo",
        "question": "What does the authentication module do?"
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "answer": "...",
            "relevant_files": [...],
            "confidence": "high|medium|low"
        }
    }
    """
    try:
        from modules.codecontext import CodeContextEngine
        
        data = request.get_json()
        repo_url = data.get('repo_url')
        question = data.get('question')
        
        if not repo_url or not question:
            return jsonify({"error": "repo_url and question are required", "success": False}), 400
        
        # Get or create client
        client = get_or_create_client(repo_url)
        
        # Create engine and ask question
        engine = CodeContextEngine()
        result = engine.ask_question(client, question)
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        return handle_error(e, "CodeContextEngine")



# ============================================
# Module 2: PR Guardian Endpoints
# ============================================

@app.route('/api/analyze/pr', methods=['POST'])
def api_analyze_pr():
    """
    Analyze a pull request.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo",
        "diff": "git diff content",
        "pr_title": "PR title",
        "pr_description": "PR description",
        "base_branch": "main",
        "head_branch": "feature-branch"
    }
    """
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        diff = data.get('diff')
        pr_title = data.get('pr_title', '')
        pr_description = data.get('pr_description', '')
        base_branch = data.get('base_branch', 'main')
        head_branch = data.get('head_branch', '')
        
        if not repo_url or not diff:
            return jsonify({"error": "repo_url and diff are required"}), 400
        
        client = get_or_create_client(repo_url)
        result = analyze_pull_request(
            client, diff, pr_title, pr_description, base_branch, head_branch
        )
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        return handle_error(e, "PR_Guardian")


@app.route('/api/analyze/pr/quick', methods=['POST'])
def api_quick_pr_check():
    """
    Quick PR check for critical issues only.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo",
        "diff": "git diff content"
    }
    """
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        diff = data.get('diff')
        
        if not repo_url or not diff:
            return jsonify({"error": "repo_url and diff are required"}), 400
        
        client = get_or_create_client(repo_url)
        result = quick_pr_check(client, diff)
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        return handle_error(e, "PR_Guardian")


@app.route('/api/pr-guardian/webhook', methods=['POST'])
def api_pr_guardian_webhook():
    """
    GitHub webhook endpoint for automated PR reviews.
    
    Receives GitHub webhook payload when PR is opened/updated,
    fetches the PR diff, runs full review, and posts comment.
    
    Webhook Events: pull_request (opened, synchronize, reopened)
    
    Headers:
        X-Hub-Signature-256: GitHub webhook signature
        X-GitHub-Event: Event type
    
    Returns:
        JSON response with review results
    """
    try:
        from modules.pr_guardian import PRGuardian
        
        # Verify webhook signature
        signature = request.headers.get('X-Hub-Signature-256', '')
        webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET', '')
        
        if webhook_secret:
            guardian = PRGuardian()
            if not guardian.verify_webhook_signature(request.data, signature, webhook_secret):
                return jsonify({
                    "error": "Invalid webhook signature",
                    "success": False
                }), 401
        
        # Parse webhook payload
        payload = request.get_json()
        
        # Check event type
        event_type = request.headers.get('X-GitHub-Event', '')
        if event_type != 'pull_request':
            return jsonify({
                "message": f"Ignoring event type: {event_type}",
                "success": True
            }), 200
        
        # Check PR action
        action = payload.get('action', '')
        if action not in ['opened', 'synchronize', 'reopened']:
            return jsonify({
                "message": f"Ignoring PR action: {action}",
                "success": True
            }), 200
        
        # Extract PR information
        pr = payload.get('pull_request', {})
        pr_number = pr.get('number')
        repo = payload.get('repository', {})
        repo_url = repo.get('html_url', '')
        
        if not pr_number or not repo_url:
            return jsonify({
                "error": "Invalid webhook payload: missing PR number or repo URL",
                "success": False
            }), 400
        
        print(f"Processing PR #{pr_number} from {repo_url}")
        
        # Initialize PR Guardian
        guardian = PRGuardian()
        
        # Fetch PR diff
        pr_diff = guardian.fetch_pr_diff(repo_url, pr_number)
        
        if pr_diff.startswith("Error:"):
            return jsonify({
                "error": pr_diff,
                "success": False
            }), 500
        
        # Get or create Bob client
        client = get_or_create_client(repo_url)
        
        # Review PR
        review = guardian.review_pr(client, pr_diff)
        
        if "error" in review:
            return jsonify({
                "error": review["error"],
                "success": False
            }), 500
        
        # Post review comment to GitHub
        comment_posted = guardian.post_github_comment(repo_url, pr_number, review)
        
        return jsonify({
            "success": True,
            "pr_number": pr_number,
            "repo_url": repo_url,
            "review": review,
            "comment_posted": comment_posted,
            "message": "PR review completed and comment posted" if comment_posted else "PR review completed but comment posting failed"
        })
    
    except Exception as e:
        return handle_error(e, "PR_Guardian_Webhook")


@app.route('/api/pr-guardian/review', methods=['POST'])
def api_pr_guardian_manual_review():
    """
    Manual PR review trigger.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo",
        "pr_number": 123,
        "post_comment": true (optional, default: false)
    }
    
    Returns:
        JSON response with review results
    """
    try:
        from modules.pr_guardian import PRGuardian
        
        data = request.get_json()
        repo_url = data.get('repo_url')
        pr_number = data.get('pr_number')
        post_comment = data.get('post_comment', False)
        
        if not repo_url or not pr_number:
            return jsonify({
                "error": "repo_url and pr_number are required",
                "success": False
            }), 400
        
        print(f"Manual review requested for PR #{pr_number} from {repo_url}")
        
        # Initialize PR Guardian
        guardian = PRGuardian()
        
        # Fetch PR diff
        pr_diff = guardian.fetch_pr_diff(repo_url, pr_number)
        
        if pr_diff.startswith("Error:"):
            return jsonify({
                "error": pr_diff,
                "success": False
            }), 500
        
        # Get or create Bob client
        client = get_or_create_client(repo_url)
        
        # Review PR
        review = guardian.review_pr(client, pr_diff)
        
        if "error" in review:
            return jsonify({
                "error": review["error"],
                "success": False
            }), 500
        
        # Optionally post comment
        comment_posted = False
        if post_comment:
            comment_posted = guardian.post_github_comment(repo_url, pr_number, review)
        
        return jsonify({
            "success": True,
            "pr_number": pr_number,
            "repo_url": repo_url,
            "review": review,
            "comment_posted": comment_posted
        })
    
    except Exception as e:
        return handle_error(e, "PR_Guardian_Manual")


# ============================================
# Module 3: Incident Whisperer Endpoints
# ============================================

@app.route('/api/analyze/incident', methods=['POST'])
def api_analyze_incident():
    """
    Analyze a bug/incident.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo",
        "error_message": "Error message",
        "stack_trace": "Stack trace (optional)",
        "code_snippet": "Code snippet (optional)",
        "logs": "Application logs (optional)",
        "environment": "Environment details (optional)",
        "additional_context": "Additional context (optional)"
    }
    """
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        error_message = data.get('error_message')
        stack_trace = data.get('stack_trace', '')
        code_snippet = data.get('code_snippet', '')
        logs = data.get('logs', '')
        environment = data.get('environment', '')
        additional_context = data.get('additional_context', '')
        
        if not repo_url or not error_message:
            return jsonify({"error": "repo_url and error_message are required"}), 400
        
        client = get_or_create_client(repo_url)
        result = analyze_incident(
            client, error_message, stack_trace, code_snippet,
            logs, environment, additional_context
        )
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        return handle_error(e, "Incident_Whisperer")


@app.route('/api/analyze/incident/quick', methods=['POST'])
def api_quick_diagnosis():
    """
    Quick error diagnosis.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo",
        "error_message": "Error message"
    }
    """
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        error_message = data.get('error_message')
        
        if not repo_url or not error_message:
            return jsonify({"error": "repo_url and error_message are required"}), 400
        
        client = get_or_create_client(repo_url)
        result = quick_error_diagnosis(client, error_message)
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        return handle_error(e, "Incident_Whisperer")


@app.route('/api/incident/webhook', methods=['POST'])
def api_incident_webhook():
    """
    Incident webhook endpoint for PagerDuty/custom alerts.
    
    Receives alert webhook, fetches recent commits, analyzes incident,
    posts to Slack, and returns analysis.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo",
        "service_name": "api-service",
        "stack_trace": "Full stack trace",
        "alert_source": "pagerduty|custom" (optional)
    }
    
    Returns:
        JSON response with incident analysis and Slack status
    """
    try:
        from modules.incident_whisperer import IncidentWhisperer
        
        data = request.get_json()
        repo_url = data.get('repo_url')
        service_name = data.get('service_name', 'Unknown Service')
        stack_trace = data.get('stack_trace')
        alert_source = data.get('alert_source', 'custom')
        
        if not repo_url or not stack_trace:
            return jsonify({
                "error": "repo_url and stack_trace are required",
                "success": False
            }), 400
        
        print(f"Processing incident webhook for {service_name} from {alert_source}")
        
        # Initialize Incident Whisperer
        whisperer = IncidentWhisperer()
        
        # Fetch recent commits
        commits = whisperer.fetch_recent_commits(repo_url, count=10)
        
        if not commits:
            return jsonify({
                "error": "Failed to fetch recent commits",
                "success": False
            }), 500
        
        # Get or create Bob client
        client = get_or_create_client(repo_url)
        
        # Analyze incident
        analysis = whisperer.analyze_incident(client, stack_trace, service_name, commits)
        
        if "error" in analysis:
            return jsonify({
                "error": analysis["error"],
                "success": False
            }), 500
        
        # Post to Slack if webhook URL is configured
        slack_posted = False
        slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        
        if slack_webhook_url:
            slack_posted = whisperer.post_slack_alert(analysis, slack_webhook_url)
        else:
            print("⚠️  Slack webhook URL not configured, skipping Slack notification")
        
        return jsonify({
            "success": True,
            "service_name": service_name,
            "analysis": analysis,
            "slack_posted": slack_posted,
            "commits_analyzed": len(commits),
            "message": "Incident analyzed and Slack alert posted" if slack_posted else "Incident analyzed (Slack not configured)"
        })
    
    except Exception as e:
        return handle_error(e, "Incident_Webhook")


@app.route('/api/incident/analyze', methods=['POST'])
def api_incident_manual_analyze():
    """
    Manual incident analysis trigger.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo",
        "stack_trace": "Full stack trace",
        "service_name": "api-service",
        "post_slack": true (optional, default: false)
    }
    
    Returns:
        JSON response with incident analysis
    """
    try:
        from modules.incident_whisperer import IncidentWhisperer
        
        data = request.get_json()
        repo_url = data.get('repo_url')
        stack_trace = data.get('stack_trace')
        service_name = data.get('service_name', 'Unknown Service')
        post_slack = data.get('post_slack', False)
        
        if not repo_url or not stack_trace:
            return jsonify({
                "error": "repo_url and stack_trace are required",
                "success": False
            }), 400
        
        print(f"Manual incident analysis requested for {service_name}")
        
        # Initialize Incident Whisperer
        whisperer = IncidentWhisperer()
        
        # Fetch recent commits
        commits = whisperer.fetch_recent_commits(repo_url, count=10)
        
        if not commits:
            return jsonify({
                "error": "Failed to fetch recent commits",
                "success": False
            }), 500
        
        # Get or create Bob client
        client = get_or_create_client(repo_url)
        
        # Analyze incident
        analysis = whisperer.analyze_incident(client, stack_trace, service_name, commits)
        
        if "error" in analysis:
            return jsonify({
                "error": analysis["error"],
                "success": False
            }), 500
        
        # Optionally post to Slack
        slack_posted = False
        if post_slack:
            slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            if slack_webhook_url:
                slack_posted = whisperer.post_slack_alert(analysis, slack_webhook_url)
            else:
                print("⚠️  Slack webhook URL not configured")
        
        return jsonify({
            "success": True,
            "service_name": service_name,
            "analysis": analysis,
            "slack_posted": slack_posted,
            "commits_analyzed": len(commits)
        })
    
    except Exception as e:
        return handle_error(e, "Incident_Manual_Analysis")


# ============================================
# Module 4: Debt Radar Endpoints
# ============================================

@app.route('/api/analyze/debt', methods=['POST'])
def api_analyze_debt():
    """
    Analyze technical debt.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo",
        "focus_areas": ["code_smells", "dependencies"] (optional),
        "include_dependencies": true (optional)
    }
    """
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        focus_areas = data.get('focus_areas')
        include_dependencies = data.get('include_dependencies', True)
        
        if not repo_url:
            return jsonify({"error": "repo_url is required"}), 400
        
        client = get_or_create_client(repo_url)
        result = analyze_technical_debt(client, focus_areas, include_dependencies)
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        return handle_error(e, "Debt_Radar")


@app.route('/api/analyze/debt/file', methods=['POST'])
def api_analyze_file_complexity():
    """
    Analyze complexity of a specific file.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo",
        "file_path": "src/app.py"
    }
    """
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        file_path = data.get('file_path')
        
        if not repo_url or not file_path:
            return jsonify({"error": "repo_url and file_path are required"}), 400
        
        client = get_or_create_client(repo_url)
        result = analyze_file_complexity(client, file_path)
        
        return jsonify({
            "success": True,
            "data": result
        })
    
    except Exception as e:
        return handle_error(e, "Debt_Radar")


@app.route('/api/debt-radar/scan', methods=['POST'])
def api_debt_radar_scan():
    """
    Run full repository scan for technical debt.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo"
    }
    
    Returns:
        Complete scan results with all scored files and repo statistics
    """
    try:
        from modules.debt_radar import DebtRadar
        
        data = request.get_json()
        repo_url = data.get('repo_url')
        
        if not repo_url:
            return jsonify({
                "error": "repo_url is required",
                "success": False
            }), 400
        
        print(f"Starting Debt Radar scan for: {repo_url}")
        
        # Get or create Bob client
        client = get_or_create_client(repo_url)
        
        # Initialize Debt Radar
        radar = DebtRadar()
        
        # Run full repository scan
        scan_results = radar.scan_repo(client)
        
        if "error" in scan_results:
            return jsonify({
                "error": scan_results["error"],
                "success": False
            }), 500
        
        # Cache the results for backlog generation
        debt_scan_cache[repo_url] = scan_results
        
        return jsonify({
            "success": True,
            "repo_url": repo_url,
            "scan_results": scan_results,
            "message": f"Scanned {scan_results.get('repo_stats', {}).get('total_files_scanned', 0)} files"
        })
    
    except Exception as e:
        return handle_error(e, "Debt_Radar_Scan")


@app.route('/api/debt-radar/backlog', methods=['GET'])
def api_debt_radar_backlog():
    """
    Get generated sprint backlog from last scan.
    
    Query Parameters:
        repo_url: Repository URL (required)
    
    Returns:
        Prioritized sprint backlog with top 10 tickets
    """
    try:
        from modules.debt_radar import DebtRadar
        
        repo_url = request.args.get('repo_url')
        
        if not repo_url:
            return jsonify({
                "error": "repo_url query parameter is required",
                "success": False
            }), 400
        
        # Check if we have cached scan results
        if repo_url not in debt_scan_cache:
            return jsonify({
                "error": "No scan results found. Please run /api/debt-radar/scan first",
                "success": False
            }), 404
        
        scan_results = debt_scan_cache[repo_url]
        
        # Initialize Debt Radar
        radar = DebtRadar()
        
        # Generate sprint backlog
        backlog = radar.generate_sprint_backlog(scan_results)
        
        return jsonify({
            "success": True,
            "repo_url": repo_url,
            "backlog": backlog,
            "total_tickets": len(backlog),
            "scan_timestamp": scan_results.get('scan_timestamp'),
            "message": f"Generated {len(backlog)} prioritized sprint tickets"
        })
    
    except Exception as e:
        return handle_error(e, "Debt_Radar_Backlog")


# ============================================
# Utility Endpoints
# ============================================

@app.route('/api/repo/info', methods=['POST'])
def api_repo_info():
    """
    Get repository information.
    
    Request Body:
    {
        "repo_url": "https://github.com/user/repo"
    }
    """
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        
        if not repo_url:
            return jsonify({"error": "repo_url is required"}), 400
        
        client = get_or_create_client(repo_url)
        summary = client.get_repo_summary()
        
        return jsonify({
            "success": True,
            "data": summary
        })
    
    except Exception as e:
        return handle_error(e, "RepoInfo")


@app.route('/api/cache/clear', methods=['POST'])
def api_clear_cache():
    """Clear the client cache."""
    try:
        client_cache.clear()
        return jsonify({
            "success": True,
            "message": "Cache cleared successfully"
        })
    except Exception as e:
        return handle_error(e, "Cache")


# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "success": False
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "success": False
    }), 500


# ============================================
# Main Entry Point
# ============================================

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("="*60)
    print("DevPulse AI - Developer Intelligence Platform")
    print("="*60)
    print(f"Server starting on http://{host}:{port}")
    print(f"Debug mode: {debug}")
    print("\nAvailable endpoints:")
    print("  GET  /                          - API information")
    print("  GET  /api/health                - Health check")
    print("  POST /api/analyze/context       - Code context analysis")
    print("  POST /api/analyze/pr            - PR review")
    print("  POST /api/analyze/incident      - Bug analysis")
    print("  POST /api/analyze/debt          - Technical debt analysis")
    print("\nPR Guardian endpoints:")
    print("  POST /api/pr-guardian/webhook   - GitHub webhook (automated)")
    print("  POST /api/pr-guardian/review    - Manual PR review trigger")
    print("\nIncident Whisperer endpoints:")
    print("  POST /api/incident/webhook      - PagerDuty/alert webhook (automated)")
    print("  POST /api/incident/analyze      - Manual incident analysis")
    print("\nDebt Radar endpoints:")
    print("  POST /api/debt-radar/scan       - Full repository scan")
    print("  GET  /api/debt-radar/backlog    - Get sprint backlog from last scan")
    print("="*60)
    
    app.run(host=host, port=port, debug=debug)

# Made with Bob
