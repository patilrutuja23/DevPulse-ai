"""
IBM Bob Client - Shared watsonx AI API Wrapper
Handles communication with IBM watsonx AI and manages repository context
"""

import os
import json
from typing import Dict, Any, Optional
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from repo_ingestion import fetch_repo_context


class BobClient:
    """
    Shared client for IBM watsonx AI with repository context management.
    
    This class provides a unified interface for all AI modules to interact
    with IBM watsonx AI while maintaining repository context.
    """
    
    def __init__(self, api_key: str, project_id: str, repo_url: str, github_token: Optional[str] = None):
        """
        Initialize BobClient with watsonx credentials and fetch repository context.
        
        Args:
            api_key: IBM watsonx API key
            project_id: IBM watsonx project ID
            repo_url: GitHub repository URL
            github_token: GitHub personal access token (optional)
        """
        self.api_key = api_key
        self.project_id = project_id
        self.repo_url = repo_url
        self.github_token = github_token
        self.repo_context = None
        self.model = None
        
        # Initialize watsonx model
        self._initialize_model()
        
        # Fetch repository context
        self._fetch_repository_context()
    
    def _initialize_model(self):
        """Initialize IBM watsonx AI model with credentials."""
        try:
            # Configure model parameters
            parameters = {
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 4000,
                GenParams.MIN_NEW_TOKENS: 1,
                GenParams.TEMPERATURE: 0.1,
                GenParams.TOP_K: 50,
                GenParams.TOP_P: 1,
                GenParams.REPETITION_PENALTY: 1.0
            }
            
            # Initialize model
            self.model = Model(
                model_id="ibm/granite-34b-code-instruct",
                params=parameters,
                credentials={
                    "apikey": self.api_key,
                    "url": "https://us-south.ml.cloud.ibm.com"
                },
                project_id=self.project_id
            )
            
            print(f"✓ IBM watsonx model initialized successfully")
            
        except Exception as e:
            print(f"✗ Error initializing watsonx model: {str(e)}")
            raise
    
    def _fetch_repository_context(self):
        """Fetch and cache repository context from GitHub."""
        try:
            print(f"Fetching repository context from: {self.repo_url}")
            self.repo_context = fetch_repo_context(self.repo_url, self.github_token)
            
            if "error" in self.repo_context:
                print(f"✗ Error fetching repo context: {self.repo_context['error']}")
            else:
                print(f"✓ Repository context loaded: {self.repo_context['total_files']} files")
                
        except Exception as e:
            print(f"✗ Error fetching repository context: {str(e)}")
            self.repo_context = {
                "error": str(e),
                "files": [],
                "tree": [],
                "total_files": 0
            }
    
    def _format_repo_context(self) -> str:
        """Format repository context for inclusion in prompts."""
        if not self.repo_context or "error" in self.repo_context:
            return "Repository context unavailable."
        
        context_parts = [
            f"Repository: {self.repo_url}",
            f"Total Files: {self.repo_context['total_files']}",
            "\nFile Tree:",
            "\n".join(f"  - {path}" for path in self.repo_context['tree'][:20]),
        ]
        
        if self.repo_context['total_files'] > 20:
            context_parts.append(f"  ... and {self.repo_context['total_files'] - 20} more files")
        
        context_parts.append("\nKey Files Content:")
        for file_info in self.repo_context['files'][:10]:
            context_parts.append(f"\n--- {file_info['path']} ---")
            context_parts.append(file_info['content'])
        
        return "\n".join(context_parts)
    
    def ask(self, system_prompt: str, user_prompt: str, include_repo_context: bool = True) -> Dict[str, Any]:
        """
        Send a prompt to IBM watsonx AI and return parsed JSON response.
        
        Args:
            system_prompt: System instructions for the AI
            user_prompt: User's specific question or request
            include_repo_context: Whether to include repository context (default: True)
        
        Returns:
            Dict containing the AI's response, parsed as JSON
        """
        try:
            # Build the complete prompt
            prompt_parts = [system_prompt]
            
            if include_repo_context and self.repo_context:
                prompt_parts.append("\n\nREPOSITORY CONTEXT:")
                prompt_parts.append(self._format_repo_context())
            
            prompt_parts.append(f"\n\nUSER REQUEST:\n{user_prompt}")
            prompt_parts.append("\n\nProvide your response as valid JSON only. No markdown, no explanations outside JSON.")
            
            full_prompt = "\n".join(prompt_parts)
            
            # Generate response
            print(f"Sending request to watsonx AI (prompt length: {len(full_prompt)} chars)...")
            response = self.model.generate_text(prompt=full_prompt)
            
            # Parse JSON response
            try:
                # Clean response - remove markdown code blocks if present
                cleaned_response = response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                
                parsed_response = json.loads(cleaned_response)
                print(f"✓ Response received and parsed successfully")
                return parsed_response
                
            except json.JSONDecodeError as e:
                print(f"✗ Failed to parse JSON response: {str(e)}")
                return {
                    "error": "Failed to parse AI response as JSON",
                    "raw_response": response[:500],
                    "parse_error": str(e)
                }
        
        except Exception as e:
            print(f"✗ Error calling watsonx API: {str(e)}")
            return {
                "error": f"API call failed: {str(e)}",
                "details": "Check your API credentials and network connection"
            }
    
    def refresh_repo_context(self):
        """Refresh the repository context (useful for updated repos)."""
        print("Refreshing repository context...")
        self._fetch_repository_context()
    
    def get_repo_summary(self) -> Dict[str, Any]:
        """Get a summary of the loaded repository context."""
        if not self.repo_context:
            return {"error": "No repository context loaded"}
        
        return {
            "repo_url": self.repo_url,
            "total_files": self.repo_context.get("total_files", 0),
            "file_types": self._count_file_types(),
            "has_error": "error" in self.repo_context
        }
    
    def _count_file_types(self) -> Dict[str, int]:
        """Count files by extension."""
        if not self.repo_context or "error" in self.repo_context:
            return {}
        
        counts = {}
        for file_info in self.repo_context.get("files", []):
            ext = file_info["path"].split(".")[-1] if "." in file_info["path"] else "no_ext"
            counts[ext] = counts.get(ext, 0) + 1
        
        return counts


# Convenience function for quick initialization
def create_bob_client(repo_url: str = None) -> BobClient:
    """
    Create a BobClient instance using environment variables.
    
    Args:
        repo_url: GitHub repository URL (uses DEMO_REPO_URL from env if not provided)
    
    Returns:
        Initialized BobClient instance
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("WATSONX_API_KEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    github_token = os.getenv("GITHUB_TOKEN")
    repo_url = repo_url or os.getenv("DEMO_REPO_URL")
    
    if not api_key or not project_id:
        raise ValueError("WATSONX_API_KEY and WATSONX_PROJECT_ID must be set in environment")
    
    if not repo_url:
        raise ValueError("repo_url must be provided or DEMO_REPO_URL must be set in environment")
    
    return BobClient(api_key, project_id, repo_url, github_token)


if __name__ == "__main__":
    # Test the client
    print("Testing BobClient...")
    try:
        client = create_bob_client()
        print("\n" + "="*60)
        print("Repository Summary:")
        print(json.dumps(client.get_repo_summary(), indent=2))
        print("="*60)
    except Exception as e:
        print(f"Test failed: {str(e)}")

# Made with Bob
