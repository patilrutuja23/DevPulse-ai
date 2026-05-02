"""
Repo Brain - Unified Intelligence Decision Engine
Combines all module outputs into a single intelligent assessment.
This is the "AI brain" that makes the final decision.
"""

from typing import Dict, List, Any, Optional


def _calculate_overall_score(
    pr_score: int,
    debt_score: int,
    has_tests: bool,
    has_ci: bool,
    has_docs: bool,
    critical_issues: int,
    high_issues: int
) -> int:
    """
    Calculate unified overall score (0-100, where 100 is best).
    Uses weighted combination of all factors.
    """
    # Start with average of PR health and inverse debt
    base_score = (pr_score + (100 - debt_score)) / 2
    
    # Apply penalties for missing critical elements
    if not has_tests:
        base_score -= 20  # Tests are critical
    if not has_ci:
        base_score -= 10  # CI/CD is important
    if not has_docs:
        base_score -= 5   # Docs are nice to have
    
    # Penalize for critical/high issues
    base_score -= (critical_issues * 8)
    base_score -= (high_issues * 4)
    
    # Ensure score stays in valid range
    return max(0, min(100, int(base_score)))


def _determine_verdict(score: int, critical_issues: int) -> str:
    """
    Determine overall verdict based on score and critical issues.
    """
    if critical_issues > 0:
        return "Critical"
    elif score >= 85:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 50:
        return "Moderate Risk"
    elif score >= 30:
        return "High Risk"
    else:
        return "Critical"


def _calculate_confidence(
    total_files: int,
    modules_analyzed: int,
    has_complete_data: bool
) -> int:
    """
    Calculate confidence level in the analysis (0-100).
    """
    confidence = 70  # Base confidence
    
    # More files = more data = higher confidence
    if total_files > 50:
        confidence += 15
    elif total_files > 20:
        confidence += 10
    elif total_files > 10:
        confidence += 5
    
    # More modules analyzed = better picture
    if modules_analyzed >= 4:
        confidence += 10
    elif modules_analyzed >= 3:
        confidence += 5
    
    # Complete data increases confidence
    if has_complete_data:
        confidence += 5
    
    return min(100, confidence)


def _extract_risk_factors(
    pr_issues: List[Dict],
    debt_issues: List[Dict],
    code_context: Dict
) -> List[Dict[str, str]]:
    """
    Extract top 3 risk factors from all modules.
    Prioritizes by severity and impact.
    """
    risks = []
    
    # Collect all critical and high severity issues
    all_issues = []
    
    # From PR Guardian
    for issue in pr_issues:
        if issue.get('severity') in ['critical', 'high']:
            all_issues.append({
                'factor': issue.get('check', 'Unknown'),
                'impact': issue.get('message', ''),
                'severity': issue.get('severity', 'medium'),
                'source': 'PR Guardian'
            })
    
    # From Debt Radar
    for issue in debt_issues:
        if issue.get('severity') in ['critical', 'high']:
            all_issues.append({
                'factor': issue.get('type', 'Unknown'),
                'impact': issue.get('detail', ''),
                'severity': issue.get('severity', 'medium'),
                'source': 'Debt Radar'
            })
    
    # Sort by severity (critical first, then high)
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    all_issues.sort(key=lambda x: severity_order.get(x['severity'], 3))
    
    # Return top 3
    return all_issues[:3]


def _extract_strengths(
    pr_passed: List[Dict],
    code_context: Dict,
    pr_score: int,
    debt_score: int
) -> List[Dict[str, str]]:
    """
    Extract top 3 strengths from analysis.
    """
    strengths = []
    
    # From PR Guardian passed checks
    for check in pr_passed[:2]:  # Top 2 passed checks
        strengths.append({
            'strength': check.get('check', 'Unknown'),
            'detail': check.get('message', ''),
            'source': 'PR Guardian'
        })
    
    # From Code Context
    tech_stack = code_context.get('techStack', [])
    if len(tech_stack) >= 3:
        strengths.append({
            'strength': 'Modern Tech Stack',
            'detail': f"Leverages {len(tech_stack)} technologies including {', '.join(tech_stack[:3])}",
            'source': 'Code Context'
        })
    
    # Architecture strength
    architecture = code_context.get('architecture', '')
    if architecture and 'Microservices' in architecture:
        strengths.append({
            'strength': 'Scalable Architecture',
            'detail': f"{architecture} enables independent scaling and deployment",
            'source': 'Code Context'
        })
    elif architecture and 'Full-Stack' in architecture:
        strengths.append({
            'strength': 'Unified Development',
            'detail': f"{architecture} provides streamlined development experience",
            'source': 'Code Context'
        })
    
    # Good health score
    if pr_score >= 80:
        strengths.append({
            'strength': 'High Code Quality',
            'detail': f"Repository health score of {pr_score}/100 indicates strong practices",
            'source': 'PR Guardian'
        })
    
    # Low debt
    if debt_score < 30:
        strengths.append({
            'strength': 'Low Technical Debt',
            'detail': f"Debt score of {debt_score}/100 shows well-maintained codebase",
            'source': 'Debt Radar'
        })
    
    return strengths[:3]


def _generate_top_fixes(
    risk_factors: List[Dict],
    debt_suggestions: List[str],
    pr_issues: List[Dict]
) -> List[Dict[str, Any]]:
    """
    Generate prioritized, actionable fixes.
    """
    fixes = []
    
    # Priority 1: Address critical risks
    for risk in risk_factors:
        if risk.get('severity') == 'critical':
            # Find corresponding suggestion
            suggestion = "Address this critical issue immediately"
            for issue in pr_issues:
                if issue.get('check') == risk.get('factor'):
                    suggestion = issue.get('suggestion', suggestion)
            
            fixes.append({
                'priority': 1,
                'action': f"Fix: {risk.get('factor')}",
                'reason': risk.get('impact', ''),
                'suggestion': suggestion,
                'impact': 'Critical'
            })
    
    # Priority 2: High severity issues
    for risk in risk_factors:
        if risk.get('severity') == 'high' and len(fixes) < 3:
            suggestion = "Address this high-priority issue"
            for issue in pr_issues:
                if issue.get('check') == risk.get('factor'):
                    suggestion = issue.get('suggestion', suggestion)
            
            fixes.append({
                'priority': 2,
                'action': f"Improve: {risk.get('factor')}",
                'reason': risk.get('impact', ''),
                'suggestion': suggestion,
                'impact': 'High'
            })
    
    # Priority 3: Top debt suggestions
    for i, suggestion in enumerate(debt_suggestions[:3]):
        if len(fixes) < 5:
            fixes.append({
                'priority': 3,
                'action': suggestion,
                'reason': 'Reduces technical debt and improves maintainability',
                'suggestion': suggestion,
                'impact': 'Medium'
            })
    
    return fixes[:5]  # Top 5 fixes


def _generate_summary(
    verdict: str,
    score: int,
    architecture: str,
    total_files: int,
    risk_count: int,
    strength_count: int
) -> str:
    """
    Generate human-readable 2-3 line summary.
    """
    # Opening statement based on verdict
    if verdict == "Excellent":
        opening = f"This is a well-maintained {architecture.lower()} project with strong development practices."
    elif verdict == "Good":
        opening = f"This {architecture.lower()} project demonstrates solid engineering with room for improvement."
    elif verdict == "Moderate Risk":
        opening = f"This {architecture.lower()} project shows moderate technical debt and quality concerns."
    elif verdict == "High Risk":
        opening = f"This {architecture.lower()} project has significant quality issues requiring immediate attention."
    else:  # Critical
        opening = f"This {architecture.lower()} project has critical issues that pose serious risks."
    
    # Risk/strength balance
    if risk_count > strength_count:
        balance = f"Identified {risk_count} risk factors that need addressing."
    elif strength_count > risk_count:
        balance = f"Found {strength_count} strengths with {risk_count} areas for improvement."
    else:
        balance = f"Balanced profile with {strength_count} strengths and {risk_count} risks."
    
    # Recommendation
    if score >= 80:
        recommendation = "Continue maintaining high standards and best practices."
    elif score >= 60:
        recommendation = "Focus on addressing high-priority issues to improve quality."
    else:
        recommendation = "Immediate action required to reduce technical debt and risks."
    
    return f"{opening} {balance} {recommendation}"


def _calculate_improvement_potential(
    current_score: int,
    has_tests: bool,
    has_ci: bool,
    has_docs: bool,
    critical_issues: int,
    high_issues: int
) -> Dict[str, Any]:
    """
    Calculate potential score improvement if top fixes are applied.
    """
    projected_score = current_score
    
    # Add points for missing critical elements
    if not has_tests:
        projected_score += 15  # Tests are most impactful
    if not has_ci:
        projected_score += 10  # CI/CD automation
    if not has_docs:
        projected_score += 5   # Documentation
    
    # Add points for fixing issues
    projected_score += min(critical_issues * 8, 20)  # Cap critical fixes at +20
    projected_score += min(high_issues * 5, 15)      # Cap high fixes at +15
    
    # Cap at 100
    projected_score = min(100, projected_score)
    
    # Calculate gain
    score_gain = projected_score - current_score
    
    # Generate message
    if score_gain >= 30:
        message = "Applying top fixes can dramatically transform project health and production readiness."
    elif score_gain >= 20:
        message = "Applying top fixes can significantly improve project health and reduce risks."
    elif score_gain >= 10:
        message = "Applying top fixes will noticeably improve code quality and maintainability."
    else:
        message = "Project is already in good shape. Minor improvements will optimize further."
    
    return {
        'currentScore': current_score,
        'projectedScore': projected_score,
        'scoreGain': f"+{score_gain} points",
        'message': message
    }


def _generate_team_risk_statement(
    overall_score: int,
    critical_issues: int,
    high_issues: int,
    has_tests: bool,
    has_ci: bool,
    verdict: str
) -> str:
    """
    Generate clear, impactful team risk statement.
    """
    # Critical risk
    if critical_issues > 0 or overall_score < 30:
        return "This project is at critical risk in production due to severe quality issues and lack of essential safeguards."
    
    # High risk
    if overall_score < 50 or (not has_tests and not has_ci):
        return "This project is at high risk in production due to lack of testing and automation pipelines."
    
    # Moderate risk
    if overall_score < 70 or not has_tests:
        return "Moderate risk: good structure but missing critical quality checks and automation."
    
    # Low risk
    if overall_score >= 85:
        return "Low risk: well-structured and production-ready with strong quality practices in place."
    
    # Good but improvable
    return "Low to moderate risk: solid foundation with minor improvements needed for production excellence."


def _determine_use_case(
    architecture: str,
    has_tests: bool,
    has_ci: bool,
    overall_score: int,
    tech_stack: List[str]
) -> Dict[str, Any]:
    """
    Determine primary use case and recommendations.
    """
    # Determine project maturity
    if overall_score >= 80 and has_tests and has_ci:
        maturity = "production-ready"
    elif overall_score >= 60 and (has_tests or has_ci):
        maturity = "development"
    else:
        maturity = "early-stage"
    
    # Determine primary use case
    tech_str = " ".join(tech_stack).lower()
    
    if maturity == "early-stage":
        if "react" in tech_str or "vue" in tech_str or "frontend" in architecture.lower():
            primary = "Best suited for early-stage frontend prototypes and MVP validation"
        else:
            primary = "Best suited for proof-of-concept and early development experimentation"
    elif maturity == "development":
        if "react" in tech_str or "vue" in tech_str or "frontend" in architecture.lower():
            primary = "Ready for active frontend development with team collaboration"
        elif "api" in tech_str or "backend" in architecture.lower():
            primary = "Ready for backend API development and integration testing"
        else:
            primary = "Ready for active development with continuous integration"
    else:  # production-ready
        if "microservices" in architecture.lower():
            primary = "Production-ready for scalable microservices deployment"
        elif "frontend" in architecture.lower():
            primary = "Production-ready for user-facing web applications"
        else:
            primary = "Production-ready for enterprise deployment and scaling"
    
    # Determine recommended use cases
    recommended = []
    
    if maturity == "early-stage":
        recommended.extend([
            "Startup MVP validation",
            "Rapid prototyping",
            "Proof of concept demos",
            "Learning and experimentation"
        ])
    elif maturity == "development":
        recommended.extend([
            "Team development projects",
            "Code quality audits",
            "PR review automation",
            "Developer onboarding"
        ])
    else:  # production-ready
        recommended.extend([
            "Production deployments",
            "Enterprise applications",
            "Customer-facing services",
            "Scalable cloud infrastructure"
        ])
    
    # Add specific recommendations based on tech stack
    if "react" in tech_str or "vue" in tech_str:
        recommended.append("Interactive web applications")
    if "docker" in tech_str:
        recommended.append("Containerized deployments")
    if "api" in tech_str or "rest" in tech_str:
        recommended.append("API-first architectures")
    
    return {
        'primary': primary,
        'recommendedFor': recommended[:5]  # Top 5
    }


def analyze_repo_brain(
    code_context: Dict[str, Any],
    pr_guardian: Dict[str, Any],
    debt_radar: Dict[str, Any],
    incident_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Unified Intelligence Decision Engine.
    
    Combines outputs from all modules into a single intelligent assessment.
    This is the "brain" that makes the final decision about repository health.
    
    Args:
        code_context: Output from analyze_code_context()
        pr_guardian: Output from analyze_pr_guardian()
        debt_radar: Output from analyze_debt_radar()
        incident_data: Optional output from analyze_incident()
    
    Returns:
        Unified intelligence response with overall score, verdict, and recommendations
    """
    # Extract key metrics
    pr_score = pr_guardian.get('score', 50)
    debt_score = debt_radar.get('debtScore', 50)
    pr_issues = pr_guardian.get('issues', [])
    pr_passed = pr_guardian.get('passed', [])
    debt_issues = debt_radar.get('issues', [])
    debt_suggestions = debt_radar.get('suggestions', [])
    
    # Count severity levels
    critical_issues = sum(1 for i in pr_issues + debt_issues if i.get('severity') == 'critical')
    high_issues = sum(1 for i in pr_issues + debt_issues if i.get('severity') == 'high')
    
    # Check for key elements
    has_tests = any('test' in check.get('check', '').lower() for check in pr_passed)
    has_ci = any('ci' in check.get('check', '').lower() for check in pr_passed)
    has_docs = any('readme' in check.get('check', '').lower() or 'doc' in check.get('check', '').lower() for check in pr_passed)
    
    # Calculate overall score
    overall_score = _calculate_overall_score(
        pr_score, debt_score, has_tests, has_ci, has_docs,
        critical_issues, high_issues
    )
    
    # Determine verdict
    verdict = _determine_verdict(overall_score, critical_issues)
    
    # Calculate confidence
    total_files = code_context.get('totalFiles', 0)
    modules_analyzed = 3 + (1 if incident_data else 0)
    has_complete_data = bool(code_context and pr_guardian and debt_radar)
    confidence = _calculate_confidence(total_files, modules_analyzed, has_complete_data)
    
    # Extract insights
    risk_factors = _extract_risk_factors(pr_issues, debt_issues, code_context)
    strengths = _extract_strengths(pr_passed, code_context, pr_score, debt_score)
    top_fixes = _generate_top_fixes(risk_factors, debt_suggestions, pr_issues)
    
    # Generate summary
    architecture = code_context.get('architecture', 'Application')
    summary = _generate_summary(
        verdict, overall_score, architecture, total_files,
        len(risk_factors), len(strengths)
    )
    
    # Calculate improvement potential
    improvement_potential = _calculate_improvement_potential(
        overall_score, has_tests, has_ci, has_docs,
        critical_issues, high_issues
    )
    
    # Generate team risk statement
    team_risk_statement = _generate_team_risk_statement(
        overall_score, critical_issues, high_issues,
        has_tests, has_ci, verdict
    )
    
    # Determine use case
    tech_stack = code_context.get('techStack', [])
    use_case = _determine_use_case(
        architecture, has_tests, has_ci, overall_score, tech_stack
    )
    
    return {
        'overallScore': overall_score,
        'verdict': verdict,
        'summary': summary,
        'confidence': confidence,
        'improvementPotential': improvement_potential,
        'teamRiskStatement': team_risk_statement,
        'useCase': use_case,
        'riskFactors': risk_factors,
        'strengths': strengths,
        'topFixes': top_fixes,
        'metrics': {
            'prHealthScore': pr_score,
            'debtScore': debt_score,
            'criticalIssues': critical_issues,
            'highIssues': high_issues,
            'totalFiles': total_files,
            'hasTests': has_tests,
            'hasCI': has_ci,
            'hasDocs': has_docs
        },
        'projectInfo': {
            'name': code_context.get('repoName', 'Unknown'),
            'architecture': architecture,
            'language': code_context.get('language', 'Unknown'),
            'techStack': tech_stack[:5]
        }
    }

# Made with Bob
