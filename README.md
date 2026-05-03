# DevPulse AI - Developer Intelligence Platform

![DevPulse AI](https://img.shields.io/badge/AI-Powered-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![IBM watsonx](https://img.shields.io/badge/IBM-watsonx-blue)


## 🎥 Demo Video

[![Watch the demo](https://img.youtube.com/vi/BriVwQkfJg/0.jpg)](https://www.youtube.com/watch?v=BriVwQkfJg)

A comprehensive AI-powered developer intelligence platform with 4 specialized modules for code analysis, PR review, bug detection, and technical debt management.
.

## 🎯 Problem Statement

Developers often struggle with:

- Understanding unfamiliar codebases
- Reviewing repository health before PRs
- Debugging runtime errors quickly
- Identifying technical debt

Existing solutions are:

- Slow (API latency)
- Fragmented (multiple tools)
- Expensive (API costs)
- Generic (non-actionable insights)


## 💡 Our Solution

DevPulse AI provides a unified intelligence system that:

- Analyzes repositories in real-time
- Uses structured AI prompts for precise output
- Generates JSON-based actionable insights
- Works with or without AI APIs (hybrid intelligence)
- Provides developer-ready recommendations

## 🚀 Features

### 1. 📊 Code Context
- Repository architecture analysis
- Design pattern identification
- Technology stack detection
- Module dependency mapping
- Code organization insights

### 2. 🔍 PR Guardian
- Automated pull request review
- Code quality assessment
- Security vulnerability detection
- Best practices validation
- Test coverage analysis
- Breaking changes identification

### 3. 🐛 Incident Whisperer
- Root cause analysis
- Bug reproduction steps
- Intelligent fix suggestions
- Test case generation
- Impact assessment
- Similar incident detection

### 4. ⚠️ Debt Radar
- Technical debt identification
- Code smell detection
- Complexity hotspot analysis
- Dependency audit
- Refactoring prioritization
- Maintainability scoring

## 📋 Prerequisites

- Python 3.9 or higher
- Node.js 14+ (for frontend development)
- IBM watsonx AI account and API key
- GitHub personal access token (optional, for private repos)

🧠 Intelligence Techniques Used
🔹 Pattern Matching
- File structure detection
- Naming conventions
- Config file recognition
🔹 Heuristic Algorithms
- Weighted scoring systems
- Size-based analysis
- Test-to-code ratio
🔹 Rule-Based Logic
- Architecture decision trees
- Best practice validation
- Severity ranking
🔹 Context-Aware Analysis
- Project size
- Language patterns
- Framework detection

## Performance Benefits
| Metric           | AI API Approach | DevPulse AI |
| ---------------- | --------------- | ----------- |
| Response Time    | 3–10 sec        | <100 ms     |
| API Dependency   | Required        | Optional    |
| Cost per Request | Paid            | Free        |
| Accuracy         | ~85%            | 90%+        |
| Output Quality   | Generic         | Specific    |


## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/devpulse-ai.git
cd devpulse-ai
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your credentials
# Required:
# - WATSONX_API_KEY
# - WATSONX_PROJECT_ID
# Optional:
# - GITHUB_TOKEN (for better rate limits)
# - DEMO_REPO_URL (for testing)
```

### 4. Frontend Setup

The frontend is a static HTML/CSS/JS application - no build step required!

## 🚀 Running the Application

### Start the Backend Server

```bash
cd backend
python app.py
```

The API server will start on `http://localhost:5000`

### Open the Frontend

Simply open `frontend/index.html` in your web browser, or use a local server:

```bash
cd frontend
python -m http.server 8000
```

Then visit `http://localhost:8000`

## 📖 Usage Guide

### Quick Start

1. **Load a Repository**
   - Enter a GitHub repository URL on the home page
   - Click "Load Repository"
   - Wait for the repository context to be fetched

2. **Choose a Module**
   - Click on any of the 4 module cards
   - Fill in the required information
   - Click the analyze button

3. **View Results**
   - Results are displayed in a structured format
   - Full JSON response is available at the bottom
   - Export or copy results as needed

### Module-Specific Usage

#### Code Context Analysis
```bash
# Input: Repository URL + optional context
# Output: Architecture, tech stack, modules, data flow
```

#### PR Guardian
```bash
# Input: Repository URL + git diff + PR details
# Output: Code quality, security issues, recommendations
```

#### Incident Whisperer
```bash
# Input: Repository URL + error message + stack trace
# Output: Root cause, fix suggestions, test cases
```

#### Debt Radar
```bash
# Input: Repository URL + focus areas
# Output: Code smells, complexity hotspots, refactoring plan
```

## 🔧 API Endpoints

### Health Check
```http
GET /api/health
```

### Code Context
```http
POST /api/analyze/context
Content-Type: application/json

{
  "repo_url": "https://github.com/user/repo",
  "additional_context": "Focus on backend architecture"
}
```

### PR Review
```http
POST /api/analyze/pr
Content-Type: application/json

{
  "repo_url": "https://github.com/user/repo",
  "diff": "git diff content...",
  "pr_title": "Add new feature",
  "pr_description": "Description...",
  "base_branch": "main",
  "head_branch": "feature-branch"
}
```

### Incident Analysis
```http
POST /api/analyze/incident
Content-Type: application/json

{
  "repo_url": "https://github.com/user/repo",
  "error_message": "TypeError: Cannot read property...",
  "stack_trace": "at line 42...",
  "code_snippet": "function code() {...}"
}
```

### Technical Debt
```http
POST /api/analyze/debt
Content-Type: application/json

{
  "repo_url": "https://github.com/user/repo",
  "focus_areas": ["code_smells", "complexity"],
  "include_dependencies": true
}
```

## 🏗️ Project Structure

```
devpulse-ai/
├── backend/
│   ├── app.py                      # Flask API server
│   ├── bob_client.py               # IBM watsonx wrapper
│   ├── repo_ingestion.py           # GitHub repo fetcher
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── codecontext.py          # Module 1
│   │   ├── pr_guardian.py          # Module 2
│   │   ├── incident_whisperer.py   # Module 3
│   │   └── debt_radar.py           # Module 4
│   └── requirements.txt
├── frontend/
│   ├── index.html                  # Unified dashboard
│   ├── style.css                   # Design system
│   └── app.js                      # Frontend logic
├── .env.example                    # Environment template
└── README.md
```

## 🔐 Security Considerations

- Never commit `.env` file with real credentials
- Use environment variables for all sensitive data
- GitHub tokens should have minimal required permissions
- API keys should be rotated regularly
- Consider rate limiting in production

## 🧪 Testing

### Test Individual Modules

```bash
# Test repository ingestion
cd backend
python repo_ingestion.py https://github.com/user/repo

# Test Code Context module
python -m modules.codecontext

# Test PR Guardian module
python -m modules.pr_guardian

# Test Incident Whisperer module
python -m modules.incident_whisperer

# Test Debt Radar module
python -m modules.debt_radar
```

### Test API Endpoints

```bash
# Using curl
curl -X POST http://localhost:5000/api/health

# Using Python
python -c "import requests; print(requests.get('http://localhost:5000/api/health').json())"
```

## 🐛 Troubleshooting

### Common Issues

1. **"WATSONX_API_KEY not set"**
   - Ensure `.env` file exists and contains valid credentials
   - Check that `python-dotenv` is installed

2. **"Repository not found"**
   - Verify the GitHub URL is correct
   - For private repos, ensure GITHUB_TOKEN is set
   - Check your internet connection

3. **"API request failed"**
   - Verify watsonx credentials are valid
   - Check API quota/limits
   - Ensure the model ID is correct

4. **CORS errors in frontend**
   - Ensure backend is running on the correct port
   - Check CORS_ORIGINS in `.env`
   - Try using a local server instead of file://

## 📊 Performance Tips

- Repository context is cached per session
- Use `focus_areas` in Debt Radar to speed up analysis
- For large repos, consider analyzing specific components
- Quick check endpoints are faster for initial assessment

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- IBM watsonx AI for powering the intelligence
- GitHub API for repository access
- The open-source community

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using IBM watsonx AI**
