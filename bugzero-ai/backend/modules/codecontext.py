"""
Module 1: CodeContext - Repository Understanding & Architecture Analysis
========================================================================

This module analyzes codebases to provide:
- Architecture overview and design patterns
- Module dependencies and relationships
- Data flow analysis
- Technology stack identification
- Code organization insights
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from bob_client import BobClient

class CodeContextEngine:
    """
    Engine for analyzing repository context and answering questions about the codebase.
    Uses BobClient to interact with IBM watsonx AI.
    """
    
    def analyze_repo(self, bob_client: BobClient) -> dict:
        """
        Analyze the repository and return structured JSON with project insights.
        
        Args:
            bob_client: Initialized BobClient instance with repository context
        
        Returns:
            Dictionary containing project analysis with keys:
            - project_name: Name of the project
            - purpose: What the system does (2-3 sentences)
            - tech_stack: List of technologies detected
            - architecture: Pattern (MVC/microservices/monolith/etc)
            - modules: List of modules with name, file, responsibility
            - data_flow: Description of how data moves through the system
            - entry_points: List of main files
            - dependencies: List of dependencies with name and purpose
            - complexity_score: Integer 1-10
        """
        system_prompt = "You are an expert software architect. Analyze the provided codebase and return ONLY valid JSON with no extra text."
        
        user_prompt = """Analyze this repository and return JSON with exactly these keys:
{
  "project_name": string,
  "purpose": string (2-3 sentences what this system does),
  "tech_stack": [list of technologies detected],
  "architecture": string (pattern: MVC/microservices/monolith/etc),
  "modules": [{"name": str, "file": str, "responsibility": str}],
  "data_flow": string (describe how data moves through the system),
  "entry_points": [str list of main files],
  "dependencies": [{"name": str, "purpose": str}],
  "complexity_score": int 1-10
}"""
        
        try:
            response = bob_client.ask(system_prompt, user_prompt, include_repo_context=True)
            
            # Add metadata
            if "error" not in response:
                response["metadata"] = {
                    "module": "CodeContextEngine",
                    "repo_url": bob_client.repo_url,
                    "total_files_analyzed": bob_client.repo_context.get('total_files', 0),
                    "analysis_type": "repository_analysis"
                }
            
            return response
        
        except Exception as e:
            return {
                "error": f"Repository analysis failed: {str(e)}",
                "module": "CodeContextEngine"
            }
    
    def ask_question(self, bob_client: BobClient, question: str) -> dict:
        """
        Ask a specific question about the codebase.
        
        Args:
            bob_client: Initialized BobClient instance with repository context
            question: Question to ask about the codebase
        
        Returns:
            Dictionary containing:
            - answer: Answer to the question
            - relevant_files: List of relevant file paths
            - confidence: 'high', 'medium', or 'low'
        """
        system_prompt = "You are a codebase expert. Answer questions about the repository. Return ONLY JSON: {'answer': str, 'relevant_files': [str], 'confidence': 'high|medium|low'}"
        
        user_prompt = f"Question about the codebase: {question}"
        
        try:
            response = bob_client.ask(system_prompt, user_prompt, include_repo_context=True)
            
            # Add metadata
            if "error" not in response:
                response["metadata"] = {
                    "module": "CodeContextEngine",
                    "repo_url": bob_client.repo_url,
                    "question": question,
                    "analysis_type": "question_answer"
                }
            
            return response
        
        except Exception as e:
            return {
                "error": f"Question answering failed: {str(e)}",
                "question": question,
                "module": "CodeContextEngine"
            }



SYSTEM_PROMPT = """You are an expert software architect and code analyst. Your task is to analyze a codebase and provide comprehensive insights about its architecture, structure, and organization.

Analyze the provided repository context and return a detailed JSON response with the following structure:

{
  "architecture": {
    "type": "string (e.g., 'Microservices', 'Monolithic', 'Layered', 'MVC', 'Serverless')",
    "description": "string - detailed description of the architecture",
    "patterns": ["array of design patterns used"],
    "strengths": ["array of architectural strengths"],
    "concerns": ["array of potential architectural concerns"]
  },
  "technology_stack": {
    "languages": ["primary programming languages"],
    "frameworks": ["frameworks and libraries"],
    "databases": ["database technologies if identifiable"],
    "tools": ["build tools, testing frameworks, etc."]
  },
  "modules": [
    {
      "name": "string - module/component name",
      "path": "string - file path or directory",
      "purpose": "string - what this module does",
      "dependencies": ["array of other modules it depends on"],
      "complexity": "string - Low/Medium/High"
    }
  ],
  "data_flow": {
    "entry_points": ["array of main entry points"],
    "flow_description": "string - how data flows through the system",
    "key_interactions": ["array of important component interactions"]
  },
  "code_organization": {
    "structure": "string - description of directory structure",
    "conventions": ["array of naming and organizational conventions"],
    "quality_score": "number 1-10",
    "recommendations": ["array of organizational improvements"]
  },
  "insights": {
    "complexity_analysis": "string - overall complexity assessment",
    "maintainability": "string - maintainability assessment",
    "scalability": "string - scalability considerations",
    "key_findings": ["array of important discoveries"]
  }
}

Be thorough, specific, and provide actionable insights. Focus on what makes this codebase unique."""


def analyze_code_context(bob_client: BobClient, additional_context: str = "") -> Dict[str, Any]:
    """
    Analyze repository architecture and code organization.
    
    Args:
        bob_client: Initialized BobClient instance with repository context
        additional_context: Optional additional context or specific questions
    
    Returns:
        Dictionary containing comprehensive code context analysis
    
    Example:
        >>> from bob_client import create_bob_client
        >>> client = create_bob_client("https://github.com/user/repo")
        >>> result = analyze_code_context(client)
        >>> print(result['architecture']['type'])
        'Microservices'
    """
    
    user_prompt = f"""Analyze this codebase and provide a comprehensive architecture and code context analysis.

Repository: {bob_client.repo_url}
Total Files: {bob_client.repo_context.get('total_files', 0)}

{additional_context if additional_context else ''}

Focus on:
1. Overall architecture and design patterns
2. Technology stack and frameworks used
3. Module structure and dependencies
4. Data flow and component interactions
5. Code organization and quality
6. Key insights and recommendations

Provide your analysis as a valid JSON object following the specified structure."""

    try:
        response = bob_client.ask(SYSTEM_PROMPT, user_prompt)
        
        # Add metadata
        if "error" not in response:
            response["metadata"] = {
                "module": "CodeContext",
                "repo_url": bob_client.repo_url,
                "total_files_analyzed": bob_client.repo_context.get('total_files', 0),
                "analysis_type": "architecture_and_organization"
            }
        
        return response
    
    except Exception as e:
        return {
            "error": f"CodeContext analysis failed: {str(e)}",
            "module": "CodeContext"
        }


def analyze_specific_component(bob_client: BobClient, component_path: str) -> Dict[str, Any]:
    """
    Analyze a specific component or module in detail.
    
    Args:
        bob_client: Initialized BobClient instance
        component_path: Path to the specific component/file to analyze
    
    Returns:
        Dictionary containing detailed component analysis
    """
    
    user_prompt = f"""Provide a detailed analysis of the specific component at: {component_path}

Focus on:
1. Purpose and responsibility of this component
2. Dependencies and relationships with other components
3. Code quality and complexity
4. Potential improvements
5. Security considerations

Return as JSON with keys: purpose, dependencies, quality_assessment, recommendations, security_notes"""

    try:
        response = bob_client.ask(SYSTEM_PROMPT, user_prompt)
        
        if "error" not in response:
            response["metadata"] = {
                "module": "CodeContext",
                "analysis_type": "component_specific",
                "component_path": component_path
            }
        
        return response
    
    except Exception as e:
        return {
            "error": f"Component analysis failed: {str(e)}",
            "component_path": component_path
        }


def compare_architectures(bob_client: BobClient, comparison_repo_url: str) -> Dict[str, Any]:
    """
    Compare the architecture of two repositories.
    
    Args:
        bob_client: BobClient for the first repository
        comparison_repo_url: URL of the second repository to compare
    
    Returns:
        Dictionary containing architectural comparison
    """
    
    user_prompt = f"""Compare the architecture of this repository with another similar project.

Current Repository: {bob_client.repo_url}
Comparison Repository: {comparison_repo_url}

Provide a comparison focusing on:
1. Architectural differences
2. Technology stack differences
3. Code organization approaches
4. Strengths and weaknesses of each
5. Recommendations for improvement

Return as JSON with keys: differences, similarities, recommendations, preferred_approach"""

    try:
        response = bob_client.ask(SYSTEM_PROMPT, user_prompt)
        
        if "error" not in response:
            response["metadata"] = {
                "module": "CodeContext",
                "analysis_type": "architecture_comparison",
                "repos_compared": [bob_client.repo_url, comparison_repo_url]
            }
        
        return response
    
    except Exception as e:
        return {
            "error": f"Architecture comparison failed: {str(e)}",
            "repos": [bob_client.repo_url, comparison_repo_url]
        }


if __name__ == "__main__":
    # Test the module
    from bob_client import create_bob_client
    import json
    
    print("Testing CodeContext Module...")
    print("="*60)
    
    try:
        # Create client
        client = create_bob_client()
        
        # Run analysis
        print("\nRunning architecture analysis...")
        result = analyze_code_context(client)
        
        # Display results
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print("✅ Analysis completed successfully!")
            print("\nArchitecture Type:", result.get('architecture', {}).get('type', 'Unknown'))
            print("\nTechnology Stack:")
            tech_stack = result.get('technology_stack', {})
            print(f"  Languages: {', '.join(tech_stack.get('languages', []))}")
            print(f"  Frameworks: {', '.join(tech_stack.get('frameworks', []))}")
            
            print("\nModules Found:", len(result.get('modules', [])))
            
            print("\n" + "="*60)
            print("Full Analysis:")
            print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

# Made with Bob
