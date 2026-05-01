/**
 * DevPulse AI - Frontend Application Logic
 * Handles UI interactions and API communication
 */

// Configuration
const API_BASE_URL = 'http://localhost:5000/api';
let currentRepoUrl = '';

// ============================================
// Utility Functions
// ============================================

/**
 * Show loading overlay
 */
function showLoading(message = 'Analyzing with AI...') {
    const overlay = document.getElementById('loading-overlay');
    const text = overlay.querySelector('.loading-text');
    text.textContent = message;
    overlay.classList.remove('hidden');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    document.getElementById('loading-overlay').classList.add('hidden');
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 200ms ease';
        setTimeout(() => toast.remove(), 200);
    }, 5000);
}

/**
 * Make API request
 */
async function apiRequest(endpoint, data) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'API request failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Format JSON for display
 */
function formatJSON(obj, indent = 0) {
    const spacing = '  '.repeat(indent);
    let html = '';
    
    if (Array.isArray(obj)) {
        if (obj.length === 0) return '[]';
        html += '[\n';
        obj.forEach((item, index) => {
            html += spacing + '  ' + formatJSON(item, indent + 1);
            if (index < obj.length - 1) html += ',';
            html += '\n';
        });
        html += spacing + ']';
    } else if (typeof obj === 'object' && obj !== null) {
        const keys = Object.keys(obj);
        if (keys.length === 0) return '{}';
        html += '{\n';
        keys.forEach((key, index) => {
            html += spacing + '  <span class="json-key">"' + key + '"</span>: ';
            html += formatJSON(obj[key], indent + 1);
            if (index < keys.length - 1) html += ',';
            html += '\n';
        });
        html += spacing + '}';
    } else if (typeof obj === 'string') {
        html += '<span class="json-string">"' + obj + '"</span>';
    } else if (typeof obj === 'number') {
        html += '<span class="json-number">' + obj + '</span>';
    } else if (typeof obj === 'boolean') {
        html += '<span class="json-boolean">' + obj + '</span>';
    } else {
        html += 'null';
    }
    
    return html;
}

/**
 * Render results in a structured way
 */
function renderResults(containerId, data) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    container.classList.remove('hidden');
    
    if (data.error) {
        container.innerHTML = `
            <div class="result-section">
                <h3 style="color: var(--danger);">❌ Error</h3>
                <p>${data.error}</p>
            </div>
        `;
        return;
    }
    
    // Render based on module type
    if (containerId === 'context-results') {
        renderContextResults(container, data);
    } else if (containerId === 'pr-results') {
        renderPRResults(container, data);
    } else if (containerId === 'incident-results') {
        renderIncidentResults(container, data);
    } else if (containerId === 'debt-results') {
        renderDebtResults(container, data);
    }
}

/**
 * Render Code Context results
 */
function renderContextResults(container, data) {
    const arch = data.architecture || {};
    const tech = data.technology_stack || {};
    const modules = data.modules || [];
    
    container.innerHTML = `
        <div class="result-section">
            <h3>🏗️ Architecture</h3>
            <div class="result-item">
                <h4>Type: ${arch.type || 'Unknown'}</h4>
                <p>${arch.description || 'No description available'}</p>
                ${arch.patterns ? `<p><strong>Patterns:</strong> ${arch.patterns.join(', ')}</p>` : ''}
            </div>
        </div>
        
        <div class="result-section">
            <h3>💻 Technology Stack</h3>
            <div class="result-item">
                ${tech.languages ? `<p><strong>Languages:</strong> ${tech.languages.join(', ')}</p>` : ''}
                ${tech.frameworks ? `<p><strong>Frameworks:</strong> ${tech.frameworks.join(', ')}</p>` : ''}
                ${tech.tools ? `<p><strong>Tools:</strong> ${tech.tools.join(', ')}</p>` : ''}
            </div>
        </div>
        
        <div class="result-section">
            <h3>📦 Modules (${modules.length})</h3>
            ${modules.slice(0, 5).map(mod => `
                <div class="result-item">
                    <h4>${mod.name}</h4>
                    <p><strong>Path:</strong> ${mod.path}</p>
                    <p>${mod.purpose}</p>
                    <span class="badge badge-${mod.complexity === 'High' ? 'high' : mod.complexity === 'Medium' ? 'medium' : 'low'}">
                        ${mod.complexity} Complexity
                    </span>
                </div>
            `).join('')}
        </div>
        
        <div class="result-section">
            <h3>📄 Full Analysis (JSON)</h3>
            <div class="code-block"><pre>${formatJSON(data)}</pre></div>
        </div>
    `;
}

/**
 * Render PR Guardian results
 */
function renderPRResults(container, data) {
    const summary = data.summary || {};
    const quality = data.code_quality || {};
    const security = data.security || {};
    
    container.innerHTML = `
        <div class="result-section">
            <h3>📊 Summary</h3>
            <div class="result-item">
                <h4>Assessment: <span class="badge badge-${summary.overall_assessment === 'APPROVED' ? 'success' : 'warning'}">${summary.overall_assessment || 'Unknown'}</span></h4>
                <p><strong>Risk Level:</strong> <span class="badge badge-${summary.risk_level?.toLowerCase() || 'low'}">${summary.risk_level || 'Unknown'}</span></p>
                <p><strong>Confidence:</strong> ${summary.confidence_score || 'N/A'}/10</p>
                <p>${summary.quick_summary || ''}</p>
            </div>
        </div>
        
        <div class="result-section">
            <h3>✅ Code Quality (Score: ${quality.score || 'N/A'}/10)</h3>
            ${quality.issues ? quality.issues.slice(0, 5).map(issue => `
                <div class="result-item">
                    <span class="badge badge-${issue.severity?.toLowerCase() || 'low'}">${issue.severity}</span>
                    <h4>${issue.type}</h4>
                    <p><strong>File:</strong> ${issue.file} ${issue.line ? `(Line ${issue.line})` : ''}</p>
                    <p>${issue.description}</p>
                    <p><strong>Suggestion:</strong> ${issue.suggestion}</p>
                </div>
            `).join('') : '<p>No issues found</p>'}
        </div>
        
        <div class="result-section">
            <h3>🔒 Security (Score: ${security.security_score || 'N/A'}/10)</h3>
            ${security.vulnerabilities && security.vulnerabilities.length > 0 ? 
                security.vulnerabilities.map(vuln => `
                    <div class="result-item">
                        <span class="badge badge-${vuln.severity?.toLowerCase() || 'low'}">${vuln.severity}</span>
                        <h4>${vuln.type}</h4>
                        <p>${vuln.description}</p>
                        <p><strong>Remediation:</strong> ${vuln.remediation}</p>
                    </div>
                `).join('') : 
                '<p>✅ No security vulnerabilities detected</p>'
            }
        </div>
        
        <div class="result-section">
            <h3>📄 Full Review (JSON)</h3>
            <div class="code-block"><pre>${formatJSON(data)}</pre></div>
        </div>
    `;
}

/**
 * Render Incident Whisperer results
 */
function renderIncidentResults(container, data) {
    const analysis = data.incident_analysis || {};
    const reproduction = data.reproduction || {};
    const fix = data.fix || {};
    
    container.innerHTML = `
        <div class="result-section">
            <h3>🔍 Root Cause Analysis</h3>
            <div class="result-item">
                <span class="badge badge-${analysis.severity?.toLowerCase() || 'medium'}">${analysis.severity || 'Unknown'}</span>
                <h4>${analysis.root_cause || 'Unknown'}</h4>
                <p><strong>Category:</strong> ${analysis.category || 'Unknown'}</p>
                <p><strong>Confidence:</strong> ${analysis.confidence || 'N/A'}/10</p>
                <p>${analysis.explanation || ''}</p>
            </div>
        </div>
        
        <div class="result-section">
            <h3>🔄 Reproduction Steps</h3>
            <div class="result-item">
                ${reproduction.steps ? `
                    <ol>
                        ${reproduction.steps.map(step => `<li>${step}</li>`).join('')}
                    </ol>
                ` : '<p>No reproduction steps available</p>'}
                <p><strong>Expected:</strong> ${reproduction.expected_behavior || 'N/A'}</p>
                <p><strong>Actual:</strong> ${reproduction.actual_behavior || 'N/A'}</p>
            </div>
        </div>
        
        <div class="result-section">
            <h3>🔧 Fix Strategy</h3>
            <div class="result-item">
                <p>${fix.strategy || 'No fix strategy available'}</p>
                ${fix.changes_needed ? fix.changes_needed.slice(0, 3).map(change => `
                    <div style="margin-top: 1rem;">
                        <p><strong>File:</strong> ${change.file}</p>
                        ${change.current_code ? `<div class="code-block"><pre>${change.current_code}</pre></div>` : ''}
                        ${change.fixed_code ? `<div class="code-block"><pre>${change.fixed_code}</pre></div>` : ''}
                        <p>${change.explanation}</p>
                    </div>
                `).join('') : ''}
            </div>
        </div>
        
        <div class="result-section">
            <h3>📄 Full Analysis (JSON)</h3>
            <div class="code-block"><pre>${formatJSON(data)}</pre></div>
        </div>
    `;
}

/**
 * Render Debt Radar results
 */
function renderDebtResults(container, data) {
    const summary = data.summary || {};
    const smells = data.code_smells || [];
    const hotspots = data.complexity_hotspots || [];
    
    container.innerHTML = `
        <div class="result-section">
            <h3>📊 Technical Debt Summary</h3>
            <div class="result-item">
                <h4>Debt Level: <span class="badge badge-${summary.overall_debt_level?.toLowerCase() || 'medium'}">${summary.overall_debt_level || 'Unknown'}</span></h4>
                <p><strong>Total Issues:</strong> ${summary.total_issues || 0}</p>
                <p><strong>Estimated Effort:</strong> ${summary.estimated_effort_days || 'N/A'} days</p>
                <p><strong>Priority Score:</strong> ${summary.priority_score || 'N/A'}/10</p>
            </div>
        </div>
        
        <div class="result-section">
            <h3>👃 Code Smells (${smells.length})</h3>
            ${smells.slice(0, 5).map(smell => `
                <div class="result-item">
                    <span class="badge badge-${smell.severity?.toLowerCase() || 'medium'}">${smell.severity}</span>
                    <h4>${smell.type}</h4>
                    <p><strong>File:</strong> ${smell.file} ${smell.line_range ? `(Lines ${smell.line_range})` : ''}</p>
                    <p>${smell.description}</p>
                    <p><strong>Impact:</strong> ${smell.impact}</p>
                    <p><strong>Suggestion:</strong> ${smell.refactoring_suggestion}</p>
                </div>
            `).join('')}
        </div>
        
        <div class="result-section">
            <h3>🔥 Complexity Hotspots (${hotspots.length})</h3>
            ${hotspots.slice(0, 5).map(hotspot => `
                <div class="result-item">
                    <h4>${hotspot.file} - ${hotspot.function}</h4>
                    <p><strong>Complexity Score:</strong> ${hotspot.complexity_score}</p>
                    <p><strong>Lines of Code:</strong> ${hotspot.lines_of_code}</p>
                    <span class="badge badge-${hotspot.refactoring_priority?.toLowerCase() || 'medium'}">
                        ${hotspot.refactoring_priority} Priority
                    </span>
                </div>
            `).join('')}
        </div>
        
        <div class="result-section">
            <h3>📄 Full Analysis (JSON)</h3>
            <div class="code-block"><pre>${formatJSON(data)}</pre></div>
        </div>
    `;
}

// ============================================
// Navigation
// ============================================

function switchModule(moduleName) {
    // Update navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.module === moduleName) {
            btn.classList.add('active');
        }
    });
    
    // Update sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`${moduleName}-section`).classList.add('active');
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================
// Event Handlers
// ============================================

// Global repo loading
document.getElementById('load-repo-btn')?.addEventListener('click', async () => {
    const repoUrl = document.getElementById('global-repo-url').value.trim();
    const statusDiv = document.getElementById('repo-status');
    
    if (!repoUrl) {
        showToast('Please enter a repository URL', 'error');
        return;
    }
    
    try {
        showLoading('Loading repository...');
        
        const result = await apiRequest('/repo/info', { repo_url: repoUrl });
        
        if (result.success) {
            currentRepoUrl = repoUrl;
            statusDiv.innerHTML = `✅ Repository loaded: ${result.data.total_files} files`;
            statusDiv.className = 'repo-status success';
            statusDiv.classList.remove('hidden');
            showToast('Repository loaded successfully!', 'success');
            
            // Pre-fill all module inputs
            document.getElementById('context-repo-url').value = repoUrl;
            document.getElementById('pr-repo-url').value = repoUrl;
            document.getElementById('incident-repo-url').value = repoUrl;
            document.getElementById('debt-repo-url').value = repoUrl;
        }
    } catch (error) {
        statusDiv.innerHTML = `❌ Error: ${error.message}`;
        statusDiv.className = 'repo-status error';
        statusDiv.classList.remove('hidden');
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
});

// Code Context Analysis
document.getElementById('analyze-context-btn')?.addEventListener('click', async () => {
    const repoUrl = document.getElementById('context-repo-url').value.trim();
    const additionalContext = document.getElementById('context-additional').value.trim();
    
    if (!repoUrl) {
        showToast('Please enter a repository URL', 'error');
        return;
    }
    
    try {
        showLoading('Analyzing code context...');
        
        const result = await apiRequest('/analyze/context', {
            repo_url: repoUrl,
            additional_context: additionalContext
        });
        
        if (result.success) {
            renderResults('context-results', result.data);
            showToast('Analysis complete!', 'success');
        }
    } catch (error) {
        renderResults('context-results', { error: error.message });
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
});

// PR Review
document.getElementById('analyze-pr-btn')?.addEventListener('click', async () => {
    const repoUrl = document.getElementById('pr-repo-url').value.trim();
    const diff = document.getElementById('pr-diff').value.trim();
    const title = document.getElementById('pr-title').value.trim();
    const description = document.getElementById('pr-description').value.trim();
    const baseBranch = document.getElementById('pr-base-branch').value.trim();
    const headBranch = document.getElementById('pr-head-branch').value.trim();
    
    if (!repoUrl || !diff) {
        showToast('Please enter repository URL and git diff', 'error');
        return;
    }
    
    try {
        showLoading('Reviewing pull request...');
        
        const result = await apiRequest('/analyze/pr', {
            repo_url: repoUrl,
            diff: diff,
            pr_title: title,
            pr_description: description,
            base_branch: baseBranch,
            head_branch: headBranch
        });
        
        if (result.success) {
            renderResults('pr-results', result.data);
            showToast('PR review complete!', 'success');
        }
    } catch (error) {
        renderResults('pr-results', { error: error.message });
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
});

// Incident Analysis
document.getElementById('analyze-incident-btn')?.addEventListener('click', async () => {
    const repoUrl = document.getElementById('incident-repo-url').value.trim();
    const errorMessage = document.getElementById('incident-error').value.trim();
    const stackTrace = document.getElementById('incident-stack').value.trim();
    const codeSnippet = document.getElementById('incident-code').value.trim();
    const logs = document.getElementById('incident-logs').value.trim();
    
    if (!repoUrl || !errorMessage) {
        showToast('Please enter repository URL and error message', 'error');
        return;
    }
    
    try {
        showLoading('Analyzing incident...');
        
        const result = await apiRequest('/analyze/incident', {
            repo_url: repoUrl,
            error_message: errorMessage,
            stack_trace: stackTrace,
            code_snippet: codeSnippet,
            logs: logs
        });
        
        if (result.success) {
            renderResults('incident-results', result.data);
            showToast('Incident analysis complete!', 'success');
        }
    } catch (error) {
        renderResults('incident-results', { error: error.message });
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
});

// Technical Debt Analysis
document.getElementById('analyze-debt-btn')?.addEventListener('click', async () => {
    const repoUrl = document.getElementById('debt-repo-url').value.trim();
    const checkboxes = document.querySelectorAll('#debt-section .checkbox-group input[type="checkbox"]:checked');
    const focusAreas = Array.from(checkboxes).map(cb => cb.value);
    
    if (!repoUrl) {
        showToast('Please enter a repository URL', 'error');
        return;
    }
    
    try {
        showLoading('Scanning technical debt...');
        
        const result = await apiRequest('/analyze/debt', {
            repo_url: repoUrl,
            focus_areas: focusAreas.length > 0 ? focusAreas : null
        });
        
        if (result.success) {
            renderResults('debt-results', result.data);
            showToast('Debt analysis complete!', 'success');
        }
    } catch (error) {
        renderResults('debt-results', { error: error.message });
        showToast(error.message, 'error');
    } finally {
        hideLoading();
    }
});

// Navigation buttons
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        switchModule(btn.dataset.module);
    });
});

// Initialize
console.log('DevPulse AI initialized');
console.log('API Base URL:', API_BASE_URL);

// Made with Bob
