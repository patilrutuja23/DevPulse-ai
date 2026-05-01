"""
Module 3: Incident Whisperer - Production Incident Root Cause Analysis
=======================================================================

This module provides intelligent incident analysis including:
- Recent commit fetching and analysis
- Root cause identification with commit correlation
- Slack alert integration with Block Kit
- Blast radius assessment
- Rollback recommendations
"""

import os
import sys
import json
import time
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bob_client import BobClient


class IncidentWhisperer:
    """
    Incident Whisperer - Production Incident Root Cause Analyzer
    
    Fetches recent commits, analyzes stack traces against code changes,
    identifies root causes, and posts rich Slack alerts.
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize Incident Whisperer.
        
        Args:
            github_token: GitHub personal access token (optional, uses env var if not provided)
        """
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            print("⚠️  Warning: No GitHub token provided. GitHub API calls will be limited.")
    
    def _parse_repo_url(self, repo_url: str) -> tuple:
        """
        Parse GitHub repository URL to extract owner and repo name.
        
        Args:
            repo_url: GitHub repository URL
        
        Returns:
            Tuple of (owner, repo)
        """
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo = path_parts[1].replace('.git', '')
            return owner, repo
        
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
    
    def fetch_recent_commits(self, repo_url: str, github_token: Optional[str] = None, count: int = 10) -> list:
        """
        Fetch recent commits with their diffs from GitHub.
        
        Args:
            repo_url: GitHub repository URL
            github_token: GitHub token (optional)
            count: Number of recent commits to fetch (default: 10)
        
        Returns:
            List of commit dictionaries with sha, message, author, timestamp, files_changed, diff
        
        Example:
            >>> whisperer = IncidentWhisperer()
            >>> commits = whisperer.fetch_recent_commits("https://github.com/user/repo", count=5)
        """
        token = github_token or self.github_token
        
        try:
            owner, repo = self._parse_repo_url(repo_url)
            
            # GitHub API endpoint for commits
            url = f"https://api.github.com/repos/{owner}/{repo}/commits"
            
            headers = {
                'Accept': 'application/vnd.github.v3+json',
            }
            
            if token:
                headers['Authorization'] = f'token {token}'
            
            params = {
                'per_page': count
            }
            
            print(f"Fetching {count} recent commits from {owner}/{repo}...")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            commits_data = response.json()
            
            # Fetch detailed info for each commit
            commits = []
            for commit_info in commits_data:
                sha = commit_info['sha']
                
                # Fetch commit details with diff
                commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
                commit_response = requests.get(commit_url, headers=headers, timeout=30)
                commit_response.raise_for_status()
                
                commit_detail = commit_response.json()
                
                # Extract files changed
                files_changed = [f['filename'] for f in commit_detail.get('files', [])]
                
                # Build diff (truncate to 500 chars)
                diff_parts = []
                for file_info in commit_detail.get('files', []):
                    patch = file_info.get('patch', '')
                    if patch:
                        diff_parts.append(f"--- {file_info['filename']} ---\n{patch}")
                
                full_diff = '\n'.join(diff_parts)
                truncated_diff = full_diff[:500] + ('...' if len(full_diff) > 500 else '')
                
                # Build commit object
                commit_obj = {
                    'sha': sha,
                    'message': commit_info['commit']['message'],
                    'author': commit_info['commit']['author']['name'],
                    'timestamp': commit_info['commit']['author']['date'],
                    'files_changed': files_changed,
                    'diff': truncated_diff
                }
                
                commits.append(commit_obj)
            
            print(f"✓ Fetched {len(commits)} commits with diffs")
            return commits
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch commits: {str(e)}"
            print(f"✗ {error_msg}")
            return []
        
        except Exception as e:
            error_msg = f"Unexpected error fetching commits: {str(e)}"
            print(f"✗ {error_msg}")
            return []
    
    def analyze_incident(self, bob_client: BobClient, stack_trace: str, 
                        service_name: str, commits: list) -> dict:
        """
        Analyze production incident to identify root cause.
        
        Args:
            bob_client: Initialized BobClient with repository context
            stack_trace: Stack trace from the incident
            service_name: Name of the affected service
            commits: List of recent commits from fetch_recent_commits()
        
        Returns:
            Dictionary with root cause analysis
        
        Example:
            >>> client = BobClient(api_key, project_id, repo_url, github_token)
            >>> whisperer = IncidentWhisperer()
            >>> commits = whisperer.fetch_recent_commits(repo_url)
            >>> analysis = whisperer.analyze_incident(client, stack_trace, "api-service", commits)
        """
        system_prompt = """You are an expert site reliability engineer and debugger. You have full repository context and recent commit history. Return ONLY valid JSON. Be extremely precise about commit hashes and line numbers."""
        
        user_prompt = f"""A production incident just fired. Identify the root cause.

SERVICE: {service_name}
STACK TRACE:
{stack_trace}

RECENT COMMITS (newest first):
{json.dumps(commits, indent=2)}

Analyze the stack trace against the commits and full codebase. Return JSON:
{{
  "root_cause_commit": "SHA of the commit that caused this, or 'unknown'",
  "root_cause_author": "author name",
  "root_cause_file": "exact file path",
  "root_cause_line": 0,
  "root_cause_explanation": "plain English: exactly what changed and why it caused this error",
  "confidence": "high|medium|low",
  "blast_radius": [{{"service": "str", "impact": "str", "severity": "critical|high|medium|low"}}],
  "suggested_fix": "specific code change to make",
  "rollback_recommended": true,
  "rollback_reason": "reason for rollback",
  "time_to_fix_estimate": "estimate"
}}

Be extremely precise. If you can identify the exact commit, provide its SHA. If not, say 'unknown'."""
        
        try:
            print(f"Analyzing incident for service: {service_name}...")
            start_time = time.time()
            
            response = bob_client.ask(system_prompt, user_prompt, include_repo_context=True)
            
            analysis_time = time.time() - start_time
            
            # Validate response structure
            if "error" in response:
                return response
            
            # Ensure all required fields exist
            required_fields = [
                "root_cause_commit", "root_cause_author", "root_cause_file",
                "root_cause_line", "root_cause_explanation", "confidence",
                "blast_radius", "suggested_fix", "rollback_recommended",
                "rollback_reason", "time_to_fix_estimate"
            ]
            
            for field in required_fields:
                if field not in response:
                    if field == "blast_radius":
                        response[field] = []
                    elif field == "root_cause_line":
                        response[field] = 0
                    elif field == "rollback_recommended":
                        response[field] = False
                    else:
                        response[field] = "Not determined"
            
            # Add metadata
            response["metadata"] = {
                "service_name": service_name,
                "analysis_time_seconds": round(analysis_time, 2),
                "commits_analyzed": len(commits),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            print(f"✓ Incident analysis completed in {analysis_time:.2f}s")
            print(f"  Root cause: {response.get('root_cause_commit', 'unknown')}")
            print(f"  Confidence: {response.get('confidence', 'unknown')}")
            
            return response
        
        except Exception as e:
            error_msg = f"Incident analysis failed: {str(e)}"
            print(f"✗ {error_msg}")
            return {
                "error": error_msg,
                "root_cause_commit": "unknown",
                "root_cause_author": "unknown",
                "root_cause_file": "unknown",
                "root_cause_line": 0,
                "root_cause_explanation": "Analysis failed due to an error",
                "confidence": "low",
                "blast_radius": [],
                "suggested_fix": "Unable to determine",
                "rollback_recommended": False,
                "rollback_reason": "Analysis incomplete",
                "time_to_fix_estimate": "Unknown"
            }
    
    def post_slack_alert(self, incident_analysis: dict, slack_webhook_url: str) -> bool:
        """
        Post incident analysis to Slack using Block Kit.
        
        Args:
            incident_analysis: Analysis dictionary from analyze_incident()
            slack_webhook_url: Slack webhook URL
        
        Returns:
            True if posted successfully, False otherwise
        
        Example:
            >>> whisperer = IncidentWhisperer()
            >>> success = whisperer.post_slack_alert(analysis, webhook_url)
        """
        if not slack_webhook_url:
            print("✗ Cannot post to Slack: No webhook URL provided")
            return False
        
        try:
            # Extract data
            commit = incident_analysis.get('root_cause_commit', 'unknown')
            author = incident_analysis.get('root_cause_author', 'unknown')
            file_path = incident_analysis.get('root_cause_file', 'unknown')
            line = incident_analysis.get('root_cause_line', 0)
            explanation = incident_analysis.get('root_cause_explanation', 'No explanation available')
            confidence = incident_analysis.get('confidence', 'unknown')
            blast_radius = incident_analysis.get('blast_radius', [])
            suggested_fix = incident_analysis.get('suggested_fix', 'No fix suggested')
            rollback = incident_analysis.get('rollback_recommended', False)
            rollback_reason = incident_analysis.get('rollback_reason', 'N/A')
            time_estimate = incident_analysis.get('time_to_fix_estimate', 'Unknown')
            analysis_time = incident_analysis.get('metadata', {}).get('analysis_time_seconds', 0)
            service_name = incident_analysis.get('metadata', {}).get('service_name', 'Unknown')
            
            # Confidence emoji
            confidence_emoji = {
                'high': '🟢',
                'medium': '🟡',
                'low': '🔴'
            }.get(confidence, '⚪')
            
            # Build Slack Block Kit message
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 Production Incident — Root Cause Found",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Service:*\n{service_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Confidence:*\n{confidence_emoji} {confidence.upper()}"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*🔍 Root Cause*\n*Commit:* `{commit[:8] if commit != 'unknown' else 'unknown'}`\n*Author:* {author}\n*File:* `{file_path}:{line}`"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📝 Explanation*\n{explanation}"
                    }
                }
            ]
            
            # Add blast radius if present
            if blast_radius:
                blast_text = "*💥 Blast Radius*\n"
                for item in blast_radius:
                    severity = item.get('severity', 'unknown')
                    severity_emoji = {
                        'critical': '🔴',
                        'high': '🟠',
                        'medium': '🟡',
                        'low': '🟢'
                    }.get(severity, '⚪')
                    service = item.get('service', 'unknown')
                    impact = item.get('impact', 'unknown')
                    blast_text += f"{severity_emoji} *{service}*: {impact}\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": blast_text
                    }
                })
            
            # Add suggested fix
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔧 Suggested Fix*\n```\n{suggested_fix}\n```"
                }
            })
            
            # Add rollback recommendation
            rollback_emoji = "✅" if rollback else "❌"
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Rollback Recommended:*\n{rollback_emoji} {'Yes' if rollback else 'No'}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time to Fix:*\n⏱️ {time_estimate}"
                    }
                ]
            })
            
            if rollback:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Rollback Reason:* {rollback_reason}"
                    }
                })
            
            # Add footer
            blocks.append({
                "type": "divider"
            })
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Powered by IBM Bob + DevPulse AI — analyzed in {analysis_time}s"
                    }
                ]
            })
            
            # Build payload
            payload = {
                "blocks": blocks,
                "text": f"🚨 Production Incident in {service_name} — Root cause identified"
            }
            
            # Post to Slack
            print(f"Posting incident alert to Slack...")
            response = requests.post(
                slack_webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            
            print(f"✓ Slack alert posted successfully")
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to post to Slack: {str(e)}")
            return False
        
        except Exception as e:
            print(f"✗ Unexpected error posting to Slack: {str(e)}")
            return False


# Legacy functions for backward compatibility
def analyze_incident(
    bob_client: BobClient,
    error_message: str,
    stack_trace: str = "",
    code_snippet: str = "",
    logs: str = "",
    environment: str = "",
    additional_context: str = ""
) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility.
    Analyze a bug/incident and provide comprehensive root cause analysis.
    """
    system_prompt = """You are an expert debugging specialist. Return ONLY valid JSON."""
    
    user_prompt = f"""Analyze this bug/incident:

ERROR MESSAGE: {error_message}
STACK TRACE: {stack_trace[:3000] if stack_trace else 'Not provided'}
CODE SNIPPET: {code_snippet[:2000] if code_snippet else 'Not provided'}
LOGS: {logs[:2000] if logs else 'Not provided'}
ENVIRONMENT: {environment if environment else 'Not specified'}
CONTEXT: {additional_context if additional_context else 'None'}

Return JSON with:
{{
  "incident_analysis": {{
    "root_cause": "str",
    "affected_components": ["array"],
    "severity": "CRITICAL|HIGH|MEDIUM|LOW",
    "category": "str",
    "confidence": 8,
    "explanation": "str"
  }},
  "fix": {{
    "strategy": "str",
    "changes_needed": [{{"file": "str", "line_range": "str", "current_code": "str", "fixed_code": "str", "explanation": "str"}}],
    "estimated_effort": "Small|Medium|Large"
  }}
}}"""
    
    try:
        response = bob_client.ask(system_prompt, user_prompt)
        if "error" not in response:
            response["metadata"] = {
                "module": "Incident_Whisperer",
                "repo_url": bob_client.repo_url
            }
        return response
    except Exception as e:
        return {
            "error": f"Incident analysis failed: {str(e)}",
            "module": "Incident_Whisperer"
        }


def quick_error_diagnosis(bob_client: BobClient, error_message: str) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility.
    Perform quick error diagnosis.
    """
    system_prompt = "You are an expert debugger. Return ONLY valid JSON."
    
    user_prompt = f"""Quick diagnosis for: {error_message}

Return JSON with:
{{
  "likely_cause": "str",
  "quick_fix": "str",
  "confidence": 8,
  "needs_deep_analysis": true
}}"""
    
    try:
        response = bob_client.ask(system_prompt, user_prompt, include_repo_context=False)
        return response
    except Exception as e:
        return {
            "error": f"Quick diagnosis failed: {str(e)}",
            "module": "Incident_Whisperer"
        }


if __name__ == "__main__":
    # Test the module
    from bob_client import create_bob_client
    
    print("Testing Incident Whisperer Module...")
    print("="*60)
    
    try:
        # Initialize
        whisperer = IncidentWhisperer()
        
        # Test repo URL parsing
        owner, repo = whisperer._parse_repo_url("https://github.com/octocat/Hello-World")
        print(f"✓ Parsed repo: {owner}/{repo}")
        
        print("\n✅ Incident Whisperer module loaded successfully!")
        print("Ready to analyze production incidents with IBM Bob.")
    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

# Made with Bob
