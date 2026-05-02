"""
Module 1: CodeContext - Intelligent Architecture Analysis
Uses advanced heuristics and pattern detection to analyze repository structure.
NO external AI APIs - pure logic-based intelligence.
"""

import os
from typing import Dict, List, Any
from collections import Counter


def _detect_architecture(files: List[str], file_tree: List[str] | None = None) -> tuple[str, str]:
    """
    Detect architecture type using intelligent pattern matching.
    Returns: (architecture_type, description)
    """
    all_files = files + (file_tree if file_tree else [])
    file_set = set(f.lower() for f in all_files)
    
    # Pattern detection
    has_frontend = any(f.endswith(('.html', '.jsx', '.tsx', '.vue', '.svelte')) for f in all_files)
    has_backend = any(f.endswith(('.py', '.java', '.go', '.rb', '.php')) for f in all_files)
    has_api = any('api' in f or 'route' in f or 'controller' in f for f in all_files)
    has_docker = 'dockerfile' in file_set or 'docker-compose.yml' in file_set
    has_serverless = any('serverless' in f or 'lambda' in f or 'function' in f for f in all_files)
    has_microservices = has_docker and any('service' in f for f in all_files)
    has_mvc = any('model' in f or 'view' in f or 'controller' in f for f in all_files)
    
    # Architecture decision tree
    if has_serverless:
        return "Serverless", "Event-driven serverless architecture with cloud functions, optimized for scalability and cost efficiency."
    
    if has_microservices:
        return "Microservices", "Distributed microservices architecture with containerized services, enabling independent deployment and scaling."
    
    if has_frontend and has_backend and has_api:
        return "Full-Stack Monolith", "Integrated full-stack application combining frontend and backend in a unified codebase with API layer."
    
    if has_backend and has_api and has_mvc:
        return "REST API / MVC", "Model-View-Controller backend service exposing RESTful APIs for client consumption."
    
    if has_frontend and not has_backend:
        return "Frontend SPA", "Single-page application focused on client-side rendering and user interface, likely consuming external APIs."
    
    if has_backend and not has_frontend:
        return "Backend Service", "Backend-focused service providing APIs, data processing, or business logic without frontend components."
    
    if any(f.endswith(('.py', '.js', '.ts', '.go', '.rs')) and 'test' not in f for f in all_files[:5]):
        return "Library / Package", "Reusable library or package designed for integration into other projects, focusing on specific functionality."
    
    return "Monolithic Application", "Traditional monolithic architecture with tightly coupled components in a single deployable unit."


def _detect_tech_stack(files: List[str], language: str) -> List[str]:
    """
    Intelligently detect technologies, frameworks, and tools from file patterns.
    """
    tech_stack = set()
    file_set = set(f.lower() for f in files)
    
    # Language detection
    if language and language != 'Unknown':
        tech_stack.add(language)
    
    # Framework detection patterns
    framework_patterns = {
        'React': ['package.json', 'react'],
        'Next.js': ['next.config', 'pages/'],
        'Vue.js': ['vue.config', '.vue'],
        'Angular': ['angular.json', '@angular'],
        'Svelte': ['svelte.config', '.svelte'],
        'Flask': ['app.py', 'flask'],
        'Django': ['manage.py', 'settings.py', 'django'],
        'FastAPI': ['fastapi', 'main.py'],
        'Express': ['express', 'app.js'],
        'Spring Boot': ['pom.xml', 'application.properties'],
        'Node.js': ['package.json', 'node_modules'],
        'TypeScript': ['.ts', '.tsx', 'tsconfig.json'],
        'Docker': ['dockerfile', 'docker-compose'],
        'Kubernetes': ['k8s/', 'deployment.yaml'],
        'PostgreSQL': ['postgres', 'pg_'],
        'MongoDB': ['mongo', 'mongoose'],
        'Redis': ['redis'],
        'GraphQL': ['graphql', '.graphql'],
        'Tailwind CSS': ['tailwind.config'],
        'Webpack': ['webpack.config'],
        'Vite': ['vite.config'],
        'Jest': ['jest.config', '.test.'],
        'Pytest': ['pytest', 'test_'],
        'GitHub Actions': ['.github/workflows'],
        'CI/CD': ['.gitlab-ci', 'jenkins', 'circleci'],
    }
    
    for tech, patterns in framework_patterns.items():
        if any(pattern in str(file_set) for pattern in patterns):
            tech_stack.add(tech)
    
    return sorted(list(tech_stack))


def _analyze_modules(files: List[str]) -> List[Dict[str, str]]:
    """
    Intelligently infer module purposes from file/folder names and patterns.
    """
    modules = []
    seen = set()
    
    # Module purpose patterns
    purpose_map = {
        'api': 'API endpoints and route handlers',
        'routes': 'Application routing and URL mapping',
        'controllers': 'Business logic controllers',
        'models': 'Data models and database schemas',
        'views': 'View templates and rendering logic',
        'components': 'Reusable UI components',
        'services': 'Business logic and service layer',
        'utils': 'Utility functions and helpers',
        'helpers': 'Helper functions and utilities',
        'config': 'Configuration files and settings',
        'middleware': 'Request/response middleware',
        'auth': 'Authentication and authorization',
        'database': 'Database connection and queries',
        'db': 'Database layer',
        'tests': 'Test suites and test cases',
        'public': 'Static assets and public files',
        'static': 'Static files (CSS, JS, images)',
        'assets': 'Application assets and resources',
        'lib': 'Core library code',
        'src': 'Source code directory',
        'dist': 'Compiled/built distribution files',
        'build': 'Build output and artifacts',
        'docs': 'Documentation files',
        'scripts': 'Automation and utility scripts',
        'migrations': 'Database migration files',
        'schemas': 'Data validation schemas',
        'types': 'TypeScript type definitions',
        'hooks': 'React hooks or Git hooks',
        'pages': 'Page components or routes',
        'layouts': 'Layout components',
        'store': 'State management (Redux, Vuex)',
        'reducers': 'Redux reducers',
        'actions': 'Redux actions',
        'context': 'React context providers',
    }
    
    for file in files[:30]:  # Analyze top 30 files
        name = file.lower().split('/')[0] if '/' in file else file.split('.')[0]
        
        if name in seen or name.startswith('.'):
            continue
        
        seen.add(name)
        
        # Match against purpose patterns
        purpose = purpose_map.get(name, None)
        
        if purpose:
            modules.append({
                'name': file.split('/')[0] if '/' in file else file,
                'purpose': purpose
            })
        elif file.endswith(('.py', '.js', '.ts', '.go', '.java')):
            # Infer from filename
            if 'test' in name:
                modules.append({'name': file, 'purpose': 'Test file'})
            elif 'config' in name:
                modules.append({'name': file, 'purpose': 'Configuration'})
            elif 'main' in name or 'index' in name or 'app' in name:
                modules.append({'name': file, 'purpose': 'Application entry point'})
    
    return modules[:10]  # Return top 10 modules


def _generate_insights(files: List[str], tech_stack: List[str], architecture: str) -> str:
    """
    Generate intelligent insights about the codebase.
    """
    insights = []
    
    # File count analysis
    file_count = len(files)
    if file_count < 10:
        insights.append(f"Compact codebase with {file_count} files, suggesting a focused or early-stage project.")
    elif file_count < 50:
        insights.append(f"Well-organized project with {file_count} files, indicating moderate complexity.")
    else:
        insights.append(f"Large-scale project with {file_count} files, suggesting enterprise-level complexity.")
    
    # Tech stack analysis
    if len(tech_stack) > 5:
        insights.append(f"Rich technology stack with {len(tech_stack)} technologies, indicating a mature and feature-rich application.")
    elif len(tech_stack) > 2:
        insights.append(f"Balanced tech stack leveraging {len(tech_stack)} core technologies for optimal development.")
    
    # Architecture insights
    if 'Microservices' in architecture:
        insights.append("Microservices architecture enables independent scaling and deployment of services.")
    elif 'Full-Stack' in architecture:
        insights.append("Full-stack approach provides unified development experience and simplified deployment.")
    elif 'Frontend' in architecture:
        insights.append("Frontend-focused architecture optimized for user experience and client-side performance.")
    
    # Testing insights
    has_tests = any('test' in f.lower() for f in files)
    if has_tests:
        insights.append("Test coverage detected, indicating commitment to code quality and reliability.")
    
    return ' '.join(insights[:3])  # Return top 3 insights


def analyze_code_context(repo_data: dict) -> dict:
    """
    Intelligent code context analysis using advanced heuristics.
    NO AI APIs - pure pattern detection and logic.
    """
    files = repo_data.get('files', [])
    name = repo_data.get('name', 'Unknown')
    lang = repo_data.get('language', 'Unknown')
    desc = repo_data.get('description', '')
    
    # Get full file tree if available
    file_tree = []
    if 'tree' in repo_data:
        file_tree = repo_data['tree']
    
    # Intelligent analysis
    architecture, arch_desc = _detect_architecture(files, file_tree)
    tech_stack = _detect_tech_stack(files + file_tree, lang)
    modules = _analyze_modules(files)
    insights = _generate_insights(files, tech_stack, architecture)
    
    return {
        'architecture': architecture,
        'architectureDescription': arch_desc,
        'techStack': tech_stack,
        'modules': modules,
        'insights': insights,
        'totalFiles': len(files),
        'repoName': name,
        'language': lang,
        'description': desc
    }

# Made with Bob
