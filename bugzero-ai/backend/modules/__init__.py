"""
DevPulse AI Modules
===================

This package contains the four core AI-powered analysis modules:

1. CodeContext - Repository understanding and architecture analysis
2. PR Guardian - Automated pull request review and quality checks
3. Incident Whisperer - Bug analysis and root cause detection
4. Debt Radar - Technical debt identification and prioritization

Each module uses the shared BobClient for IBM watsonx AI integration.
"""

from .codecontext import analyze_code_context
from .pr_guardian import analyze_pull_request
from .incident_whisperer import analyze_incident
from .debt_radar import analyze_technical_debt

__all__ = [
    'analyze_code_context',
    'analyze_pull_request',
    'analyze_incident',
    'analyze_technical_debt'
]

__version__ = '1.0.0'

# Made with Bob
