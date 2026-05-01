"""
Module 2: PR Guardian - Automated Pull Request Review with GitHub Integration
==============================================================================

This module provides comprehensive PR review including:
- GitHub API integration for fetching PR diffs
- Automated PR review with IBM Bob
- GitHub comment posting
- Webhook handling for automated reviews
- Security vulnerability detection
- Test coverage analysis
"""

import os
import sys
import json
import hmac
import hashlib
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bob_client import BobClient


class PRGuardian:
    """
    PR Guardian - Automated Pull Request Review System
    
    Integrates with GitHub to fetch PR diffs, analyze them using IBM Bob,
    and post comprehensive review comments back to GitHub.
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize PR Guardian.
        
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
        
        Example:
            >>> _parse_repo_url("https://github.com/user/repo")
            ('user', 'repo')
        """
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) >= 2:
            owner = path_parts[0]
            repo = path_parts[1].replace('.git', '')
            return owner, repo
        
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
    
    def fetch_pr_diff(self, repo_url: str, pr_number: int, github_token: Optional[str] = None) -> str:
        """
        Fetch PR diff from GitHub API.
        
        Args:
            repo_url: GitHub repository URL
            pr_number: Pull request number
            github_token: GitHub token (optional, uses instance token if not provided)
        
        Returns:
            Concatenated diff string with file paths as headers (max 3000 chars)
        
        Example:
            >>> guardian = PRGuardian()
            >>> diff = guardian.fetch_pr_diff("https://github.com/user/repo", 123)
        """
        token = github_token or self.github_token
        
        try:
            owner, repo = self._parse_repo_url(repo_url)
            
            # GitHub API endpoint for PR files
            url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
            
            headers = {
                'Accept': 'application/vnd.github.v3+json',
            }
            
            if token:
                headers['Authorization'] = f'token {token}'
            
            print(f"Fetching PR #{pr_number} files from {owner}/{repo}...")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            files = response.json()
            
            # Build concatenated diff with file headers
            diff_parts = []
            total_chars = 0
            max_chars = 3000
            
            # Process files in reverse order (newest first) so we can truncate oldest
            for file_info in reversed(files):
                filename = file_info.get('filename', 'unknown')
                patch = file_info.get('patch', '')
                status = file_info.get('status', 'modified')
                
                # Create file header
                file_header = f"\n{'='*60}\nFile: {filename} ({status})\n{'='*60}\n"
                file_content = file_header + patch + "\n"
                
                # Check if adding this file would exceed limit
                if total_chars + len(file_content) > max_chars:
                    # Truncate if we're at the limit
                    remaining = max_chars - total_chars
                    if remaining > 100:  # Only add if we have meaningful space
                        diff_parts.append(file_content[:remaining] + "\n... [truncated]")
                    break
                
                diff_parts.append(file_content)
                total_chars += len(file_content)
            
            # Reverse back to original order (oldest to newest)
            diff_parts.reverse()
            
            full_diff = ''.join(diff_parts)
            
            print(f"✓ Fetched {len(files)} files, diff size: {len(full_diff)} chars")
            return full_diff
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch PR diff: {str(e)}"
            print(f"✗ {error_msg}")
            return f"Error: {error_msg}"
        
        except Exception as e:
            error_msg = f"Unexpected error fetching PR diff: {str(e)}"
            print(f"✗ {error_msg}")
            return f"Error: {error_msg}"
    
    def review_pr(self, bob_client: BobClient, pr_diff: str) -> dict:
        """
        Review PR using IBM Bob with full repository context.
        
        Args:
            bob_client: Initialized BobClient with repository context
            pr_diff: PR diff string
        
        Returns:
            Dictionary with review results in specified JSON structure
        
        Example:
            >>> client = BobClient(api_key, project_id, repo_url, github_token)
            >>> guardian = PRGuardian()
            >>> diff = guardian.fetch_pr_diff(repo_url, 123)
            >>> review = guardian.review_pr(client, diff)
        """
        system_prompt = """You are a senior software engineer doing a thorough pull request review. You have full repository context. Return ONLY valid JSON."""
        
        user_prompt = f"""Review this pull request diff against the full codebase context.

PR Diff:
{pr_diff}

Return JSON with exactly this structure:
{{
  "summary": "2 sentences overall assessment",
  "verdict": "approve|request_changes|comment",
  "critical": [{{"file": "str", "line": 0, "issue": "str", "fix": "str"}}],
  "warnings": [{{"file": "str", "issue": "str", "suggestion": "str"}}],
  "missing_tests": [{{"function": "str", "test_cases": ["str"]}}],
  "impact": [{{"file": "str", "risk": "high|medium|low", "reason": "str"}}],
  "security_issues": [{{"type": "str", "description": "str", "severity": "critical|high|medium"}}],
  "score": 7
}}

Be thorough and specific. Focus on critical issues, security, and missing tests."""
        
        try:
            print("Sending PR diff to IBM Bob for review...")
            response = bob_client.ask(system_prompt, user_prompt, include_repo_context=True)
            
            # Validate response structure
            if "error" in response:
                return response
            
            # Ensure all required fields exist
            required_fields = ["summary", "verdict", "critical", "warnings", 
                             "missing_tests", "impact", "security_issues", "score"]
            
            for field in required_fields:
                if field not in response:
                    response[field] = [] if field not in ["summary", "verdict", "score"] else (
                        "No summary provided" if field == "summary" else 
                        "comment" if field == "verdict" else 5
                    )
            
            print(f"✓ PR review completed. Verdict: {response.get('verdict', 'unknown')}")
            return response
        
        except Exception as e:
            error_msg = f"PR review failed: {str(e)}"
            print(f"✗ {error_msg}")
            return {
                "error": error_msg,
                "summary": "Review failed due to an error",
                "verdict": "comment",
                "critical": [],
                "warnings": [],
                "missing_tests": [],
                "impact": [],
                "security_issues": [],
                "score": 0
            }
    
    def post_github_comment(self, repo_url: str, pr_number: int, review: dict, 
                           github_token: Optional[str] = None) -> bool:
        """
        Post review as a GitHub comment.
        
        Args:
            repo_url: GitHub repository URL
            pr_number: Pull request number
            review: Review dictionary from review_pr()
            github_token: GitHub token (optional)
        
        Returns:
            True if comment posted successfully, False otherwise
        
        Example:
            >>> guardian = PRGuardian()
            >>> success = guardian.post_github_comment(repo_url, 123, review)
        """
        token = github_token or self.github_token
        
        if not token:
            print("✗ Cannot post comment: No GitHub token available")
            return False
        
        try:
            owner, repo = self._parse_repo_url(repo_url)
            
            # Format review as markdown
            comment = self._format_review_comment(review)
            
            # GitHub API endpoint for issue comments (PRs are issues)
            url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
            
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'Authorization': f'token {token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'body': comment
            }
            
            print(f"Posting review comment to PR #{pr_number}...")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            print(f"✓ Review comment posted successfully")
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to post comment: {str(e)}")
            return False
        
        except Exception as e:
            print(f"✗ Unexpected error posting comment: {str(e)}")
            return False
    
    def _format_review_comment(self, review: dict) -> str:
        """
        Format review dictionary into markdown GitHub comment.
        
        Args:
            review: Review dictionary
        
        Returns:
            Formatted markdown string
        """
        verdict = review.get('verdict', 'comment')
        score = review.get('score', 0)
        summary = review.get('summary', 'No summary available')
        
        # Verdict emoji
        verdict_emoji = {
            'approve': '✅',
            'request_changes': '⚠️',
            'comment': '💬'
        }.get(verdict, '💬')
        
        # Score badge
        if score >= 8:
            score_badge = f"🟢 **{score}/10** (Excellent)"
        elif score >= 6:
            score_badge = f"🟡 **{score}/10** (Good)"
        elif score >= 4:
            score_badge = f"🟠 **{score}/10** (Needs Work)"
        else:
            score_badge = f"🔴 **{score}/10** (Critical Issues)"
        
        # Build comment
        lines = [
            "## 🤖 PR Guardian Review (IBM Bob)",
            "",
            f"{verdict_emoji} **Verdict:** {verdict.replace('_', ' ').title()}",
            f"{score_badge}",
            "",
            "### 📋 Summary",
            summary,
            ""
        ]
        
        # Critical Issues
        critical = review.get('critical', [])
        if critical:
            lines.append("### 🚨 Critical Issues")
            for issue in critical:
                file = issue.get('file', 'unknown')
                line = issue.get('line', 0)
                problem = issue.get('issue', 'No description')
                fix = issue.get('fix', 'No fix suggested')
                lines.append(f"- **{file}:{line}** - {problem}")
                lines.append(f"  - 💡 **Fix:** {fix}")
            lines.append("")
        
        # Security Issues
        security = review.get('security_issues', [])
        if security:
            lines.append("### 🔒 Security Issues")
            for issue in security:
                severity = issue.get('severity', 'unknown')
                issue_type = issue.get('type', 'Unknown')
                description = issue.get('description', 'No description')
                severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡'}.get(severity, '⚪')
                lines.append(f"- {severity_emoji} **{severity.upper()}** - {issue_type}")
                lines.append(f"  - {description}")
            lines.append("")
        
        # Warnings
        warnings = review.get('warnings', [])
        if warnings:
            lines.append("### ⚠️ Warnings")
            for warning in warnings:
                file = warning.get('file', 'unknown')
                issue = warning.get('issue', 'No description')
                suggestion = warning.get('suggestion', 'No suggestion')
                lines.append(f"- **{file}** - {issue}")
                lines.append(f"  - 💡 {suggestion}")
            lines.append("")
        
        # Missing Tests
        missing_tests = review.get('missing_tests', [])
        if missing_tests:
            lines.append("### 🧪 Missing Tests")
            for test in missing_tests:
                function = test.get('function', 'unknown')
                test_cases = test.get('test_cases', [])
                lines.append(f"- **{function}**")
                for case in test_cases:
                    lines.append(f"  - {case}")
            lines.append("")
        
        # Impact Analysis
        impact = review.get('impact', [])
        if impact:
            lines.append("### 📊 Impact Analysis")
            for item in impact:
                file = item.get('file', 'unknown')
                risk = item.get('risk', 'unknown')
                reason = item.get('reason', 'No reason provided')
                risk_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(risk, '⚪')
                lines.append(f"- {risk_emoji} **{file}** ({risk.upper()} risk)")
                lines.append(f"  - {reason}")
            lines.append("")
        
        # Footer
        lines.extend([
            "---",
            f"*Powered by IBM watsonx.ai (Granite Code) | PR Guardian v1.0*"
        ])
        
        return '\n'.join(lines)
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Verify GitHub webhook signature.
        
        Args:
            payload: Raw request body as bytes
            signature: X-Hub-Signature-256 header value
            secret: Webhook secret
        
        Returns:
            True if signature is valid, False otherwise
        """
        if not signature or not secret:
            return False
        
        # GitHub sends signature as "sha256=<hash>"
        if not signature.startswith('sha256='):
            return False
        
        expected_signature = signature.split('=')[1]
        
        # Calculate HMAC
        mac = hmac.new(secret.encode(), payload, hashlib.sha256)
        calculated_signature = mac.hexdigest()
        
        # Constant-time comparison
        return hmac.compare_digest(calculated_signature, expected_signature)


# Standalone functions for backward compatibility
def analyze_pull_request(
    bob_client: BobClient,
    diff: str,
    pr_title: str = "",
    pr_description: str = "",
    base_branch: str = "main",
    head_branch: str = ""
) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility.
    Analyze a pull request and provide comprehensive review.
    """
    guardian = PRGuardian()
    return guardian.review_pr(bob_client, diff)


def quick_pr_check(bob_client: BobClient, diff: str) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility.
    Perform a quick PR check focusing on critical issues only.
    """
    system_prompt = "You are a senior software engineer. Return ONLY valid JSON."
    
    user_prompt = f"""Quick PR check for critical issues only:

{diff[:5000]}

Return JSON with:
{{
  "critical_issues": ["array of critical issues"],
  "can_merge": true/false,
  "quick_notes": "brief assessment"
}}"""
    
    try:
        response = bob_client.ask(system_prompt, user_prompt)
        return response
    except Exception as e:
        return {
            "error": f"Quick PR check failed: {str(e)}",
            "critical_issues": [],
            "can_merge": False,
            "quick_notes": "Review failed"
        }


if __name__ == "__main__":
    # Test the module
    from bob_client import create_bob_client
    
    print("Testing PR Guardian Module...")
    print("="*60)
    
    # Test with environment variables
    try:
        # Initialize
        guardian = PRGuardian()
        
        # Test repo URL parsing
        owner, repo = guardian._parse_repo_url("https://github.com/octocat/Hello-World")
        print(f"✓ Parsed repo: {owner}/{repo}")
        
        # Test diff fetching (using a public repo)
        print("\nTesting PR diff fetch...")
        # Note: This will only work if the PR exists
        # diff = guardian.fetch_pr_diff("https://github.com/octocat/Hello-World", 1)
        # print(f"Diff preview: {diff[:200]}...")
        
        print("\n✅ PR Guardian module loaded successfully!")
        print("Ready to review pull requests with IBM Bob.")
    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

# Made with Bob
