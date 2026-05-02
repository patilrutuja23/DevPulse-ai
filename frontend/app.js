// DevPulse AI — Frontend Logic
const API = 'http://127.0.0.1:5000';

let currentRepoUrl = '';
let currentRepoData = null;

// ── Utilities ─────────────────────────────────────────────────────────────────

function $(id) { return document.getElementById(id); }

function showLoading(msg = 'Analyzing...') {
  $('loading-text').textContent = msg;
  $('loading').classList.remove('hidden');
  $('results').classList.add('hidden');
}

function hideLoading() {
  $('loading').classList.add('hidden');
}

function showError(msg) {
  hideLoading();
  $('results').innerHTML = `<div class="result-error">❌ ${msg}</div>`;
  $('results').classList.remove('hidden');
}

function setRepoStatus(msg, type) {
  const el = $('repo-status');
  el.textContent = msg;
  el.className = `repo-status repo-status-${type}`;
  el.classList.remove('hidden');
}

function enableModuleButtons() {
  ['btn-context', 'btn-pr', 'btn-debt', 'btn-incident'].forEach(id => {
    $(id).disabled = false;
  });
}

async function apiFetch(endpoint, body) {
  const res = await fetch(`${API}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(json.error || `HTTP ${res.status}`);
  return json.data;
}

// ── Load Repository ───────────────────────────────────────────────────────────

async function loadRepo() {
  const url = $('repo-url').value.trim();
  if (!url) { setRepoStatus('Please enter a GitHub repository URL.', 'error'); return; }

  $('load-btn').disabled = true;
  setRepoStatus('Loading repository...', 'info');
  $('repo-card').classList.add('hidden');
  $('results').classList.add('hidden');
  $('incident-form').classList.add('hidden');

  try {
    const data = await apiFetch('/load-repo', { repo_url: url });

    currentRepoUrl = url;
    currentRepoData = data;

    // Populate repo card
    $('rc-name').textContent = data.full_name || data.name;
    $('rc-desc').textContent = data.description;
    $('rc-lang').textContent = data.language;
    $('rc-stars').textContent = `⭐ ${data.stars.toLocaleString()}`;
    $('rc-files').textContent = `📁 ${data.files.length} items`;

    $('repo-card').classList.remove('hidden');
    enableModuleButtons();
    setRepoStatus(`✅ Repository loaded — ${data.files.length} items found`, 'success');
  } catch (e) {
    setRepoStatus(`❌ ${e.message}`, 'error');
  } finally {
    $('load-btn').disabled = false;
  }
}

// Allow Enter key on repo input
$('repo-url').addEventListener('keydown', e => { if (e.key === 'Enter') loadRepo(); });

// ── Module Runner ─────────────────────────────────────────────────────────────

async function runModule(endpoint) {
  if (!currentRepoUrl) return;

  const labels = {
    'code-context': 'Analyzing architecture...',
    'pr-review': 'Running health checks...',
    'debt': 'Scanning for technical debt...',
  };

  showLoading(labels[endpoint] || 'Analyzing...');
  $('incident-form').classList.add('hidden');

  try {
    const data = await apiFetch(`/${endpoint}`, { repo_url: currentRepoUrl });
    hideLoading();

    if (endpoint === 'code-context') renderCodeContext(data);
    else if (endpoint === 'pr-review') renderPRGuardian(data);
    else if (endpoint === 'debt') renderDebtRadar(data);
  } catch (e) {
    showError(e.message);
  }
}

// ── Incident Form ─────────────────────────────────────────────────────────────

function showIncidentForm() {
  $('incident-form').classList.remove('hidden');
  $('results').classList.add('hidden');
  $('incident-form').scrollIntoView({ behavior: 'smooth' });
}

function hideIncidentForm() {
  $('incident-form').classList.add('hidden');
}

async function runIncident() {
  const errorMsg = $('error-msg').value.trim();
  const codeSnippet = $('code-snippet').value.trim();

  if (!errorMsg) { alert('Please enter an error message.'); return; }
  if (!codeSnippet) { alert('Please enter a code snippet.'); return; }

  showLoading('Diagnosing bug...');
  $('incident-form').classList.add('hidden');

  try {
    const data = await apiFetch('/incident', { error_message: errorMsg, code_snippet: codeSnippet });
    hideLoading();
    renderIncident(data);
  } catch (e) {
    showError(e.message);
  }
}

// ── Renderers ─────────────────────────────────────────────────────────────────

function card(title, content) {
  return `<div class="result-card"><h3 class="result-card-title">${title}</h3>${content}</div>`;
}

function badge(text, cls) {
  return `<span class="badge badge-${cls}">${text}</span>`;
}

function severityBadge(sev) {
  const map = { critical: 'critical', high: 'high', medium: 'medium', low: 'low' };
  return badge(sev.toUpperCase(), map[sev.toLowerCase()] || 'low');
}

function showResults(html) {
  $('results').innerHTML = html;
  $('results').classList.remove('hidden');
  $('results').scrollIntoView({ behavior: 'smooth' });
}

// --- Code Context ---
function renderCodeContext(d) {
  const techPills = (d.techStack || []).map(t => `<span class="pill">${t}</span>`).join('');
  const moduleRows = (d.modules || []).map(m =>
    `<tr><td class="td-name">${m.name}</td><td class="td-desc">${m.purpose}</td></tr>`
  ).join('');

  showResults(`
    <div class="results-header">
      <h2>📊 Code Context — ${d.repoName}</h2>
    </div>
    ${card('🏗️ Architecture', `
      <p class="arch-type">${d.architecture}</p>
      <p class="arch-desc">${d.architectureDescription}</p>
    `)}
    ${card('💻 Tech Stack', `<div class="pill-group">${techPills || '<em>Not detected</em>'}</div>`)}
    ${moduleRows ? card('📦 Detected Modules & Files', `
      <table class="result-table">
        <thead><tr><th>Name</th><th>Purpose</th></tr></thead>
        <tbody>${moduleRows}</tbody>
      </table>
    `) : ''}
    ${card('📈 Stats', `
      <div class="stat-row">
        <div class="stat"><span class="stat-val">${d.totalFiles}</span><span class="stat-label">Root Items</span></div>
        <div class="stat"><span class="stat-val">${(d.techStack || []).length}</span><span class="stat-label">Technologies</span></div>
        <div class="stat"><span class="stat-val">${(d.modules || []).length}</span><span class="stat-label">Modules Found</span></div>
      </div>
    `)}
  `);
}

// --- PR Guardian ---
function renderPRGuardian(d) {
  const scoreClass = d.score >= 80 ? 'score-good' : d.score >= 60 ? 'score-warn' : 'score-bad';

  const issueRows = (d.issues || []).map(i => `
    <div class="check-item check-fail">
      <div class="check-top">
        ${severityBadge(i.severity)}
        <strong>${i.check}</strong>
      </div>
      <p>${i.message}</p>
      <p class="suggestion">💡 ${i.suggestion}</p>
    </div>
  `).join('');

  const passedRows = (d.passed || []).map(p => `
    <div class="check-item check-pass">
      <span class="check-tick">✅</span> <strong>${p.check}</strong> — ${p.message}
    </div>
  `).join('');

  showResults(`
    <div class="results-header">
      <h2>🔍 PR Guardian — Repository Health</h2>
    </div>
    ${card('📊 Health Score', `
      <div class="score-display">
        <span class="score-number ${scoreClass}">${d.score}</span>
        <span class="score-label">/ 100 — ${d.verdict}</span>
      </div>
      <div class="score-bar-bg"><div class="score-bar ${scoreClass}" style="width:${d.score}%"></div></div>
      <p class="score-meta">${d.passedCount} checks passed · ${d.issueCount} issues found</p>
    `)}
    ${d.issues.length ? card(`⚠️ Issues (${d.issueCount})`, issueRows) : ''}
    ${d.passed.length ? card(`✅ Passed (${d.passedCount})`, passedRows) : ''}
  `);
}

// --- Incident Whisperer ---
function renderIncident(d) {
  const steps = (d.reproductionSteps || []).map((s, i) => `<li>${s}</li>`).join('');

  showResults(`
    <div class="results-header">
      <h2>🐛 Incident Whisperer</h2>
      <div>${severityBadge(d.severity)} <span class="badge badge-type">${d.errorType}</span></div>
    </div>
    ${card('🎯 Root Cause', `<p class="root-cause-text">${d.rootCause}</p>`)}
    ${card('📖 Explanation', `<p>${d.explanation}</p>`)}
    ${card('💡 Fix', `<p>${d.fix}</p>`)}
    ${d.updatedCode ? card('✅ Updated Code', `<pre class="code-block">${escHtml(d.updatedCode)}</pre>`) : ''}
    ${steps ? card('🔄 Reproduction Steps', `<ol class="steps-list">${steps}</ol>`) : ''}
  `);
}

// --- Debt Radar ---
function renderDebtRadar(d) {
  const debtClass = { Low: 'score-good', Medium: 'score-warn', High: 'score-bad', Critical: 'score-bad' }[d.debtLevel] || 'score-warn';
  const debtPct = Math.min(100, d.debtScore);

  const issueRows = (d.issues || []).map(i => `
    <div class="check-item check-fail">
      <div class="check-top">
        ${severityBadge(i.severity)}
        <strong>${i.type}</strong>
        ${i.file ? `<code class="file-tag">${i.file}</code>` : ''}
      </div>
      <p>${i.detail}</p>
      <p class="suggestion">💡 ${i.suggestion}</p>
    </div>
  `).join('');

  const suggestionList = (d.suggestions || []).map(s => `<li>${s}</li>`).join('');

  showResults(`
    <div class="results-header">
      <h2>⚠️ Debt Radar — Technical Debt Analysis</h2>
    </div>
    ${card('📊 Debt Score', `
      <div class="score-display">
        <span class="score-number ${debtClass}">${d.debtScore}</span>
        <span class="score-label">/ 100 — ${d.debtLevel} Debt</span>
      </div>
      <div class="score-bar-bg"><div class="score-bar ${debtClass}" style="width:${debtPct}%"></div></div>
      <div class="severity-counts">
        ${Object.entries(d.severityCounts || {}).map(([k, v]) =>
          v > 0 ? `<span class="badge badge-${k}">${k}: ${v}</span>` : ''
        ).join('')}
      </div>
    `)}
    ${d.issues.length ? card(`🔍 Issues Found (${d.totalIssues})`, issueRows) : card('✅ No Issues', '<p>No technical debt issues detected.</p>')}
    ${suggestionList ? card('📋 Prioritized Suggestions', `<ol class="steps-list">${suggestionList}</ol>`) : ''}
  `);
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function escHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
