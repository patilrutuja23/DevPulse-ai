"""
README Generator Module
Generates professional README.md content based on repository analysis.
"""

from typing import Dict, Any, List


def generate_readme(
    repo_data: Dict[str, Any],
    code_context: Dict[str, Any],
    pr_guardian: Dict[str, Any],
    debt_radar: Dict[str, Any]
) -> str:
    """
    Generate a professional README.md content.
    
    Args:
        repo_data: Repository metadata from load_repo()
        code_context: Output from analyze_code_context()
        pr_guardian: Output from analyze_pr_guardian()
        debt_radar: Output from analyze_debt_radar()
    
    Returns:
        Formatted README.md content as string
    """
    repo_name = repo_data.get('name', 'Project')
    description = repo_data.get('description', 'A software project')
    language = repo_data.get('language', 'Unknown')
    tech_stack = code_context.get('techStack', [])
    architecture = code_context.get('architecture', 'Application')
    
    # Extract key metrics
    pr_score = pr_guardian.get('score', 0)
    debt_score = debt_radar.get('debtScore', 0)
    issues = pr_guardian.get('issues', []) + debt_radar.get('issues', [])
    
    # Build README sections
    readme = f"""# {repo_name}

{description}

## 📋 Overview

This is a {architecture.lower()} built with {language}. The project demonstrates modern development practices and follows industry standards.

## 🛠 Tech Stack

"""
    
    # Add tech stack
    if tech_stack:
        for tech in tech_stack[:10]:
            readme += f"- {tech}\n"
    else:
        readme += f"- {language}\n"
    
    readme += "\n## ✨ Features\n\n"
    
    # Add features based on architecture
    if "Frontend" in architecture or "SPA" in architecture:
        readme += """- Interactive user interface
- Responsive design
- Modern component architecture
- Client-side routing
"""
    elif "Backend" in architecture or "API" in architecture:
        readme += """- RESTful API endpoints
- Data processing and validation
- Business logic implementation
- Database integration
"""
    elif "Full-Stack" in architecture:
        readme += """- Complete frontend and backend integration
- API endpoints and UI components
- End-to-end functionality
- Unified development experience
"""
    else:
        readme += """- Modular code structure
- Clean architecture
- Scalable design
- Industry best practices
"""
    
    # Add quality metrics
    readme += f"""
## 📊 Code Quality

- **Health Score:** {pr_score}/100
- **Technical Debt:** {debt_score}/100
- **Architecture:** {architecture}

"""
    
    # Add issues if any
    critical_issues = [i for i in issues if i.get('severity') == 'critical']
    high_issues = [i for i in issues if i.get('severity') == 'high']
    
    if critical_issues or high_issues:
        readme += "## ⚠️ Known Issues\n\n"
        
        if critical_issues:
            readme += "### Critical\n"
            for issue in critical_issues[:3]:
                readme += f"- {issue.get('check') or issue.get('type')}: {issue.get('message') or issue.get('detail')}\n"
            readme += "\n"
        
        if high_issues:
            readme += "### High Priority\n"
            for issue in high_issues[:3]:
                readme += f"- {issue.get('check') or issue.get('type')}: {issue.get('message') or issue.get('detail')}\n"
            readme += "\n"
    
    # Add improvements section
    suggestions = debt_radar.get('suggestions', [])
    if suggestions:
        readme += "## 🚀 Recommended Improvements\n\n"
        for i, suggestion in enumerate(suggestions[:5], 1):
            readme += f"{i}. {suggestion}\n"
        readme += "\n"
    
    # Add setup instructions
    readme += """## 🏃 Getting Started

### Prerequisites

"""
    
    if "node" in " ".join(tech_stack).lower() or "react" in " ".join(tech_stack).lower():
        readme += "- Node.js (v14 or higher)\n- npm or yarn\n"
    elif language.lower() == "python":
        readme += "- Python 3.8+\n- pip\n"
    elif language.lower() == "java":
        readme += "- Java JDK 11+\n- Maven or Gradle\n"
    else:
        readme += f"- {language} runtime\n"
    
    readme += """
### Installation

```bash
# Clone the repository
git clone <repository-url>

# Install dependencies
"""
    
    if "node" in " ".join(tech_stack).lower():
        readme += "npm install\n"
    elif language.lower() == "python":
        readme += "pip install -r requirements.txt\n"
    else:
        readme += "# Follow language-specific setup\n"
    
    readme += """```

### Running the Project

```bash
"""
    
    if "react" in " ".join(tech_stack).lower() or "vite" in " ".join(tech_stack).lower():
        readme += "npm run dev\n"
    elif "flask" in " ".join(tech_stack).lower():
        readme += "python app.py\n"
    elif "express" in " ".join(tech_stack).lower():
        readme += "npm start\n"
    else:
        readme += "# Follow project-specific run instructions\n"
    
    readme += """```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

*This README was generated by DevPulse AI*
"""
    
    return readme


# Made with Bob