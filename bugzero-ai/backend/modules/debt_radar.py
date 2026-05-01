"""
Module 4: Debt Radar - Technical Debt Detection & Sprint Backlog Generation
============================================================================

This module identifies and analyzes technical debt including:
- File-level debt scoring across multiple dimensions
- Repository-wide scanning
- Sprint backlog generation with prioritization
- Downstream impact analysis
"""

import os
import sys
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bob_client import BobClient


class DebtRadar:
    """
    Debt Radar - Technical Debt Scanner and Sprint Backlog Generator
    
    Scores files for technical debt, scans entire repositories,
    and generates prioritized sprint backlogs.
    """
    
    def __init__(self):
        """Initialize Debt Radar."""
        pass
    
    def score_file(self, bob_client: BobClient, file_path: str, file_content: str) -> dict:
        """
        Score a single file for technical debt across multiple dimensions.
        
        Args:
            bob_client: Initialized BobClient with repository context
            file_path: Path to the file
            file_content: Content of the file
        
        Returns:
            Dictionary with debt scores and findings
        
        Example:
            >>> radar = DebtRadar()
            >>> client = BobClient(api_key, project_id, repo_url, github_token)
            >>> score = radar.score_file(client, "src/app.py", file_content)
        """
        system_prompt = """You are a code quality expert. Score technical debt precisely. Return ONLY valid JSON."""
        
        user_prompt = f"""Score this file for technical debt on each dimension 0-100 (0=no debt, 100=worst possible).

FILE: {file_path}
CONTENT:
{file_content[:3000]}

Return JSON:
{{
  "file": "{file_path}",
  "scores": {{
    "complexity": 0,
    "duplication": 0,
    "coupling": 0,
    "test_coverage": 0,
    "staleness": 0
  }},
  "debt_index": 0,
  "findings": [{{
    "severity": "critical|high|medium|low",
    "description": "str",
    "effort_hours": 0.0,
    "fix_suggestion": "str"
  }}],
  "downstream_impact": ["list of files that likely depend on this one"]
}}

Calculate debt_index as: complexity*0.3 + duplication*0.2 + coupling*0.2 + test_coverage*0.2 + staleness*0.1
Be precise with scores. Consider actual code patterns, not just file size."""
        
        try:
            print(f"Scoring file: {file_path}...")
            response = bob_client.ask(system_prompt, user_prompt, include_repo_context=True)
            
            # Validate response structure
            if "error" in response:
                return response
            
            # Ensure required fields exist
            if "file" not in response:
                response["file"] = file_path
            
            if "scores" not in response:
                response["scores"] = {
                    "complexity": 50,
                    "duplication": 50,
                    "coupling": 50,
                    "test_coverage": 50,
                    "staleness": 50
                }
            
            if "debt_index" not in response:
                scores = response["scores"]
                response["debt_index"] = int(
                    scores.get("complexity", 50) * 0.3 +
                    scores.get("duplication", 50) * 0.2 +
                    scores.get("coupling", 50) * 0.2 +
                    scores.get("test_coverage", 50) * 0.2 +
                    scores.get("staleness", 50) * 0.1
                )
            
            if "findings" not in response:
                response["findings"] = []
            
            if "downstream_impact" not in response:
                response["downstream_impact"] = []
            
            print(f"✓ Scored {file_path}: debt_index={response['debt_index']}")
            return response
        
        except Exception as e:
            error_msg = f"File scoring failed: {str(e)}"
            print(f"✗ {error_msg}")
            return {
                "error": error_msg,
                "file": file_path,
                "scores": {
                    "complexity": 0,
                    "duplication": 0,
                    "coupling": 0,
                    "test_coverage": 0,
                    "staleness": 0
                },
                "debt_index": 0,
                "findings": [],
                "downstream_impact": []
            }
    
    def scan_repo(self, bob_client: BobClient) -> dict:
        """
        Scan entire repository for technical debt.
        
        Args:
            bob_client: Initialized BobClient with repository context
        
        Returns:
            Dictionary with all scored files and repo-level statistics
        
        Example:
            >>> radar = DebtRadar()
            >>> client = BobClient(api_key, project_id, repo_url, github_token)
            >>> results = radar.scan_repo(client)
        """
        try:
            print(f"Starting repository scan for: {bob_client.repo_url}")
            start_time = datetime.utcnow()
            
            # Get files from repo context
            if not bob_client.repo_context or "error" in bob_client.repo_context:
                return {
                    "error": "Repository context not available",
                    "files": [],
                    "repo_stats": {},
                    "scan_timestamp": start_time.isoformat()
                }
            
            files_to_scan = bob_client.repo_context.get('files', [])
            
            if not files_to_scan:
                return {
                    "error": "No files found in repository context",
                    "files": [],
                    "repo_stats": {},
                    "scan_timestamp": start_time.isoformat()
                }
            
            print(f"Scanning {len(files_to_scan)} files...")
            
            # Score each file
            scored_files = []
            total_findings = 0
            
            for file_info in files_to_scan:
                file_path = file_info.get('path', 'unknown')
                file_content = file_info.get('content', '')
                
                # Skip empty files or very small files
                if len(file_content.strip()) < 10:
                    continue
                
                score_result = self.score_file(bob_client, file_path, file_content)
                
                if "error" not in score_result:
                    scored_files.append(score_result)
                    total_findings += len(score_result.get('findings', []))
            
            # Sort by debt_index descending
            scored_files.sort(key=lambda x: x.get('debt_index', 0), reverse=True)
            
            # Calculate repo-level stats
            if scored_files:
                avg_debt = sum(f.get('debt_index', 0) for f in scored_files) / len(scored_files)
                most_critical_file = scored_files[0] if scored_files else None
                
                # Calculate average scores
                avg_complexity = sum(f.get('scores', {}).get('complexity', 0) for f in scored_files) / len(scored_files)
                avg_duplication = sum(f.get('scores', {}).get('duplication', 0) for f in scored_files) / len(scored_files)
                avg_coupling = sum(f.get('scores', {}).get('coupling', 0) for f in scored_files) / len(scored_files)
                avg_test_coverage = sum(f.get('scores', {}).get('test_coverage', 0) for f in scored_files) / len(scored_files)
                avg_staleness = sum(f.get('scores', {}).get('staleness', 0) for f in scored_files) / len(scored_files)
            else:
                avg_debt = 0
                most_critical_file = None
                avg_complexity = avg_duplication = avg_coupling = avg_test_coverage = avg_staleness = 0
            
            repo_stats = {
                "total_files_scanned": len(scored_files),
                "avg_debt_index": round(avg_debt, 2),
                "most_critical_file": most_critical_file.get('file') if most_critical_file else None,
                "most_critical_debt_index": most_critical_file.get('debt_index') if most_critical_file else 0,
                "total_findings": total_findings,
                "avg_scores": {
                    "complexity": round(avg_complexity, 2),
                    "duplication": round(avg_duplication, 2),
                    "coupling": round(avg_coupling, 2),
                    "test_coverage": round(avg_test_coverage, 2),
                    "staleness": round(avg_staleness, 2)
                },
                "files_with_critical_findings": sum(
                    1 for f in scored_files 
                    if any(finding.get('severity') == 'critical' for finding in f.get('findings', []))
                ),
                "files_with_high_debt": sum(1 for f in scored_files if f.get('debt_index', 0) > 70)
            }
            
            end_time = datetime.utcnow()
            scan_duration = (end_time - start_time).total_seconds()
            
            print(f"✓ Repository scan completed in {scan_duration:.2f}s")
            print(f"  Files scanned: {len(scored_files)}")
            print(f"  Average debt index: {avg_debt:.2f}")
            print(f"  Total findings: {total_findings}")
            
            return {
                "files": scored_files,
                "repo_stats": repo_stats,
                "scan_timestamp": start_time.isoformat(),
                "scan_duration_seconds": round(scan_duration, 2)
            }
        
        except Exception as e:
            error_msg = f"Repository scan failed: {str(e)}"
            print(f"✗ {error_msg}")
            return {
                "error": error_msg,
                "files": [],
                "repo_stats": {},
                "scan_timestamp": datetime.utcnow().isoformat()
            }
    
    def generate_sprint_backlog(self, scan_results: dict) -> list:
        """
        Generate prioritized sprint backlog from scan results.
        
        Args:
            scan_results: Results from scan_repo()
        
        Returns:
            List of top 10 prioritized sprint tickets
        
        Example:
            >>> radar = DebtRadar()
            >>> backlog = radar.generate_sprint_backlog(scan_results)
        """
        try:
            print("Generating sprint backlog...")
            
            files = scan_results.get('files', [])
            
            if not files:
                print("⚠️  No files to generate backlog from")
                return []
            
            # Extract all findings from all files
            all_findings = []
            
            for file_data in files:
                file_path = file_data.get('file', 'unknown')
                findings = file_data.get('findings', [])
                downstream_impact = file_data.get('downstream_impact', [])
                
                for finding in findings:
                    # Create ticket
                    ticket = {
                        'file': file_path,
                        'severity': finding.get('severity', 'low'),
                        'description': finding.get('description', 'No description'),
                        'effort_hours': finding.get('effort_hours', 1.0),
                        'fix_suggestion': finding.get('fix_suggestion', 'No suggestion'),
                        'downstream_impact_count': len(downstream_impact)
                    }
                    all_findings.append(ticket)
            
            # Calculate priority scores
            severity_weights = {
                'critical': 4,
                'high': 3,
                'medium': 2,
                'low': 1
            }
            
            for ticket in all_findings:
                severity = ticket['severity']
                severity_weight = severity_weights.get(severity, 1)
                downstream_count = ticket['downstream_impact_count']
                effort_hours = max(ticket['effort_hours'], 0.1)  # Avoid division by zero
                
                # Priority score: (severity_weight * downstream_impact_count) / effort_hours
                # Higher score = higher priority
                priority_score = (severity_weight * max(downstream_count, 1)) / effort_hours
                ticket['priority_score'] = round(priority_score, 2)
            
            # Sort by priority score descending
            all_findings.sort(key=lambda x: x['priority_score'], reverse=True)
            
            # Take top 10
            top_tickets = all_findings[:10]
            
            # Format as sprint tickets
            sprint_backlog = []
            for i, ticket in enumerate(top_tickets, 1):
                sprint_ticket = {
                    'rank': i,
                    'title': f"Fix {ticket['severity']} issue in {ticket['file']}",
                    'file': ticket['file'],
                    'severity': ticket['severity'],
                    'effort_hours': ticket['effort_hours'],
                    'description': ticket['description'],
                    'fix_suggestion': ticket['fix_suggestion'],
                    'priority_score': ticket['priority_score'],
                    'downstream_impact_count': ticket['downstream_impact_count']
                }
                sprint_backlog.append(sprint_ticket)
            
            print(f"✓ Generated sprint backlog with {len(sprint_backlog)} tickets")
            return sprint_backlog
        
        except Exception as e:
            error_msg = f"Sprint backlog generation failed: {str(e)}"
            print(f"✗ {error_msg}")
            return []


# Legacy functions for backward compatibility
def analyze_technical_debt(
    bob_client: BobClient,
    focus_areas: Optional[list] = None,
    include_dependencies: bool = True
) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility.
    Analyze technical debt across the entire codebase.
    """
    system_prompt = """You are an expert software architect and code quality specialist. Return ONLY valid JSON."""
    
    focus_text = ""
    if focus_areas:
        focus_text = f"\nFocus specifically on: {', '.join(focus_areas)}"
    
    user_prompt = f"""Analyze this codebase for technical debt.

Repository: {bob_client.repo_url}
Total Files: {bob_client.repo_context.get('total_files', 0) if bob_client.repo_context else 0}
{focus_text}

Return JSON with:
{{
  "summary": {{
    "overall_debt_level": "LOW|MEDIUM|HIGH|CRITICAL",
    "total_issues": 0,
    "estimated_effort_days": 0,
    "priority_score": 5
  }},
  "code_smells": [{{
    "type": "str",
    "severity": "CRITICAL|HIGH|MEDIUM|LOW",
    "file": "str",
    "description": "str",
    "refactoring_suggestion": "str"
  }}],
  "complexity_hotspots": [{{
    "file": "str",
    "function": "str",
    "complexity_score": 0,
    "issues": ["array"]
  }}]
}}"""
    
    try:
        response = bob_client.ask(system_prompt, user_prompt)
        if "error" not in response:
            response["metadata"] = {
                "module": "Debt_Radar",
                "repo_url": bob_client.repo_url
            }
        return response
    except Exception as e:
        return {
            "error": f"Technical debt analysis failed: {str(e)}",
            "module": "Debt_Radar"
        }


def analyze_file_complexity(bob_client: BobClient, file_path: str) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility.
    Analyze complexity of a specific file.
    """
    system_prompt = "You are a code quality expert. Return ONLY valid JSON."
    
    user_prompt = f"""Analyze complexity of: {file_path}

Return JSON with:
{{
  "functions": [{{
    "name": "str",
    "complexity": 0,
    "loc": 0,
    "issues": ["array"]
  }}],
  "overall_complexity": 0,
  "refactoring_priority": "HIGH|MEDIUM|LOW",
  "suggestions": ["array"]
}}"""
    
    try:
        response = bob_client.ask(system_prompt, user_prompt)
        return response
    except Exception as e:
        return {
            "error": f"File complexity analysis failed: {str(e)}",
            "file_path": file_path
        }


if __name__ == "__main__":
    # Test the module
    from bob_client import create_bob_client
    
    print("Testing Debt Radar Module...")
    print("="*60)
    
    try:
        # Initialize
        radar = DebtRadar()
        
        print("\n✅ Debt Radar module loaded successfully!")
        print("Ready to scan repositories for technical debt.")
    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

# Made with Bob
