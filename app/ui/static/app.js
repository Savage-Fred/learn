/**
 * Savage-Fred / learn — Local-First Single-Page Application (Zero-CDN)
 * Vanilla ES Module Architecture
 */

// =============================================================================
// 1. STATE STORE
// =============================================================================
const Store = {
  state: {
    theme: localStorage.getItem('learn_theme') || 'light',
    apiToken: localStorage.getItem('learn_api_token') || '',
    activeView: 'dashboard',
    topics: [],
    pinnedTopics: [],
    userRatings: {},
    activeTopic: null,
    activeTopicDetail: null,
    activeQuizSession: null,
    activeInterviewSession: null,
    telemetrySummary: null,
    selectedTopicIndex: 0,
    connectionStatus: 'connecting',
  },

  listeners: new Set(),

  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  },

  setState(partial) {
    Object.assign(this.state, partial);
    this.listeners.forEach(fn => fn(this.state));
  },

  setTheme(theme) {
    this.state.theme = theme;
    localStorage.setItem('learn_theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
    this.setState({ theme });
  },

  setApiToken(token) {
    this.state.apiToken = token;
    localStorage.setItem('learn_api_token', token);
    this.setState({ apiToken: token });
  }
};

// =============================================================================
// 2. API CLIENT
// =============================================================================
const API = {
  baseUrl: '/api',

  getHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (Store.state.apiToken) {
      headers['Authorization'] = `Bearer ${Store.state.apiToken}`;
      headers['X-Learn-Token'] = Store.state.apiToken;
    }
    return headers;
  },

  async request(endpoint, options = {}) {
    options.headers = { ...this.getHeaders(), ...(options.headers || {}) };
    let res;
    try {
      res = await fetch(`${this.baseUrl}${endpoint}`, options);
      if (res.status === 404 && !endpoint.startsWith('/v1')) {
        res = await fetch(`/api/v1${endpoint}`, options);
      }
    } catch (err) {
      Store.setState({ connectionStatus: 'offline' });
      throw new Error(`Network error: ${err.message}`);
    }

    if (res.status === 401) {
      Store.setState({ connectionStatus: 'unauthorized' });
      document.getElementById('modal-auth')?.showModal();
      throw new Error('Unauthorized: please provide your LEARN_API_TOKEN');
    }

    if (!res.ok) {
      const errPayload = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errPayload.detail || errPayload.message || 'Request failed');
    }

    return res.json();
  },

  async checkStatus() {
    try {
      const data = await this.request('/v1/status');
      const isLoopback = !data.data_dir.includes('[protected]');
      Store.setState({
        connectionStatus: isLoopback ? 'connected_local' : 'connected_tailnet'
      });
      return data;
    } catch {
      return this.request('/health');
    }
  },

  async listTopics(domain = 'all') {
    return this.request(`/topics?domain=${domain}`);
  },

  async getTopicDetail(domain, topicSlug) {
    return this.request(`/topics/${domain}/${topicSlug}`);
  },

  async getPinnedTopics() {
    return this.request('/topics/pinned');
  },

  async pinTopic(domain, topicSlug, priority = 'high', notes = '') {
    return this.request(`/topics/${domain}/${topicSlug}/pin`, {
      method: 'POST',
      body: JSON.stringify({ priority, notes }),
    });
  },

  async unpinTopic(domain, topicSlug) {
    return this.request(`/topics/${domain}/${topicSlug}/pin`, {
      method: 'DELETE',
    });
  },

  async recordDurableLearning(domain, topicSlug, payload) {
    return this.request(`/topics/${domain}/${topicSlug}/learnings`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async startQuiz(topicId, initialLevel = 'starter') {
    return this.request('/quiz/start', {
      method: 'POST',
      body: JSON.stringify({ topic_id: topicId, initial_level: initialLevel }),
    });
  },

  async submitQuizTurn(turnData) {
    return this.request('/quiz/turn', {
      method: 'POST',
      body: JSON.stringify(turnData),
    });
  },

  async getRatings() {
    return this.request('/quiz/ratings');
  },

  async startInterview(interviewData) {
    return this.request('/interview/start', {
      method: 'POST',
      body: JSON.stringify(interviewData),
    });
  },

  async submitInterviewTurn(sessionId, turnData) {
    return this.request(`/interview/${sessionId}/turn`, {
      method: 'POST',
      body: JSON.stringify(turnData),
    });
  },

  async getScorecard(sessionId) {
    return this.request(`/interview/${sessionId}/scorecard`);
  },

  async analyzeResumeFit(data) {
    return this.request('/resume/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getTelemetrySummary() {
    return this.request('/telemetry/summary');
  }
};

// =============================================================================
// 3. TOAST NOTIFICATIONS
// =============================================================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 250);
  }, 3000);
}

// =============================================================================
// 4. SVG RENDERER (RADAR CHARTS & METERS)
// =============================================================================
const SVGRenderer = {
  renderRadarChart(scores, size = 260) {
    const center = size / 2;
    const radius = center - 35;
    const dimensions = ['decomposition', 'execution', 'architecture', 'resilience', 'communication'];
    const totalPoints = dimensions.length;
    const angleStep = (Math.PI * 2) / totalPoints;

    // Web background rings
    let ringsSvg = '';
    for (let r = 1; r <= 5; r++) {
      const ringRadius = (radius / 5) * r;
      let ringPoints = [];
      for (let i = 0; i < totalPoints; i++) {
        const angle = i * angleStep - Math.PI / 2;
        ringPoints.push(`${center + ringRadius * Math.cos(angle)},${center + ringRadius * Math.sin(angle)}`);
      }
      ringsSvg += `<polygon points="${ringPoints.join(' ')}" fill="none" stroke="var(--border-light)" stroke-width="1"/>`;
    }

    // Radial axes & labels
    let axesSvg = '';
    dimensions.forEach((dim, i) => {
      const angle = i * angleStep - Math.PI / 2;
      const x = center + radius * Math.cos(angle);
      const y = center + radius * Math.sin(angle);
      axesSvg += `<line x1="${center}" y1="${center}" x2="${x}" y2="${y}" class="radar-axis"/>`;

      const labelDist = radius + 18;
      const lx = center + labelDist * Math.cos(angle);
      const ly = center + labelDist * Math.sin(angle);
      const shortName = dim.charAt(0).toUpperCase() + dim.slice(1, 4);
      axesSvg += `<text x="${lx}" y="${ly}" text-anchor="middle" dominant-baseline="middle" font-size="10" fill="var(--text-secondary)" font-family="var(--font-mono)">${shortName}</text>`;
    });

    // Score polygon
    const polygonPoints = dimensions.map((dim, i) => {
      const val = Math.max(1.0, Math.min(5.0, scores[dim] || 3.0));
      const r = (radius / 5) * val;
      const angle = i * angleStep - Math.PI / 2;
      return `${center + r * Math.cos(angle)},${center + r * Math.sin(angle)}`;
    });

    return `
      <svg viewBox="0 0 ${size} ${size}" class="radar-chart-svg">
        ${ringsSvg}
        ${axesSvg}
        <polygon points="${polygonPoints.join(' ')}" class="radar-polygon"/>
      </svg>
    `;
  },

  renderFitGauge(percentage, size = 160) {
    const strokeWidth = 10;
    const center = size / 2;
    const radius = center - strokeWidth;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;

    return `
      <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
        <circle cx="${center}" cy="${center}" r="${radius}" class="gauge-circle-bg" stroke-width="${strokeWidth}"/>
        <circle cx="${center}" cy="${center}" r="${radius}" class="gauge-circle-fill" stroke-width="${strokeWidth}"
          stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
          transform="rotate(-90 ${center} ${center})"/>
        <text x="${center}" y="${center + 6}" text-anchor="middle" font-size="28" font-weight="700" fill="var(--text-primary)" font-family="var(--font-mono)">
          ${percentage}%
        </text>
      </svg>
    `;
  }
};

// =============================================================================
// 5. VIEW CONTROLLERS
// =============================================================================

// Switch active view
function showView(viewId) {
  document.querySelectorAll('.app-view').forEach(view => {
    view.classList.remove('active');
    view.hidden = true;
  });
  document.querySelectorAll('.nav-link-btn').forEach(btn => {
    btn.classList.remove('active');
  });

  const targetView = document.getElementById(`view-${viewId}`);
  const targetNav = document.getElementById(`nav-${viewId}`);
  if (targetView) {
    targetView.classList.add('active');
    targetView.hidden = false;
  }
  if (targetNav) {
    targetNav.classList.add('active');
  }
  Store.setState({ activeView: viewId });
}

// Render Dashboard
function renderDashboard() {
  const tbody = document.getElementById('topic-table-body');
  if (!tbody) return;

  const topics = Store.state.topics;
  if (!topics || topics.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px;">No topics found.</td></tr>';
    return;
  }

  tbody.innerHTML = topics.map((t, index) => {
    const isSelected = index === Store.state.selectedTopicIndex;
    const rating = (t.user_rating || 0.0).toFixed(1);
    const pinClass = t.pinned ? 'btn-primary' : 'btn-secondary';
    const pinText = t.pinned ? 'Pinned' : 'Pin (p)';

    return `
      <tr class="topic-row ${isSelected ? 'selected' : ''}" data-index="${index}" data-domain="${t.domain}" data-slug="${t.slug}">
        <td>
          <div style="font-weight:600;">${t.title}</div>
          <div style="font-size:11px; color:var(--text-muted); font-family:var(--font-mono);">${t.slug}</div>
        </td>
        <td>
          <span class="badge badge-company">${t.domain}</span>
        </td>
        <td>
          <div style="display:flex; gap:4px; flex-wrap:wrap;">
            ${(t.role_tracks || []).slice(0, 2).map(r => `<span class="badge badge-l4" style="font-size:10px;">${r}</span>`).join('')}
          </div>
        </td>
        <td>
          <div style="display:flex; align-items:center; gap:6px;">
            <div class="rating-gauge-bar">
              <div class="rating-gauge-fill" style="width:${(t.user_rating || 0.0) / 5.0 * 100}%;"></div>
            </div>
            <span style="font-family:var(--font-mono); font-size:11px;">${rating}</span>
          </div>
        </td>
        <td>
          <div style="display:flex; gap:4px;">
            <button class="btn btn-secondary btn-sm btn-action-dive" data-domain="${t.domain}" data-slug="${t.slug}">Deep Dive</button>
            <button class="btn ${pinClass} btn-sm btn-action-pin" data-domain="${t.domain}" data-slug="${t.slug}">${pinText}</button>
          </div>
        </td>
      </tr>
    `;
  }).join('');

  // Row click listeners
  tbody.querySelectorAll('.topic-row').forEach(row => {
    row.addEventListener('click', (e) => {
      if (e.target.closest('button')) return;
      const domain = row.dataset.domain;
      const slug = row.dataset.slug;
      location.hash = `#topic/${domain}/${slug}`;
    });
  });

  // Action button listeners
  tbody.querySelectorAll('.btn-action-dive').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const domain = btn.dataset.domain;
      const slug = btn.dataset.slug;
      location.hash = `#topic/${domain}/${slug}`;
    });
  });

  tbody.querySelectorAll('.btn-action-pin').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const domain = btn.dataset.domain;
      const slug = btn.dataset.slug;
      await togglePinTopic(domain, slug);
    });
  });
}

// Render Pinned Bar
function renderPinnedBar() {
  const container = document.getElementById('pinned-list');
  if (!container) return;

  const pins = Store.state.pinnedTopics;
  if (!pins || pins.length === 0) {
    container.innerHTML = '<span class="text-muted" style="font-size:11px;">No pinned topics. Press \'p\' to pin.</span>';
    return;
  }

  container.innerHTML = pins.map(p => {
    const slug = p.topic_id || p.topic_slug;
    const domain = p.domain || 'general';
    const prio = p.priority || 'high';
    return `
      <div class="pinned-chip" data-domain="${domain}" data-slug="${slug}">
        <span class="pinned-priority-dot ${prio}"></span>
        <span>${slug}</span>
        <button class="unpin-btn" data-domain="${domain}" data-slug="${slug}" title="Unpin">×</button>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.pinned-chip').forEach(chip => {
    chip.addEventListener('click', (e) => {
      if (e.target.closest('.unpin-btn')) return;
      const domain = chip.dataset.domain;
      const slug = chip.dataset.slug;
      location.hash = `#topic/${domain}/${slug}`;
    });
  });

  container.querySelectorAll('.unpin-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const domain = btn.dataset.domain;
      const slug = btn.dataset.slug;
      try {
        await API.unpinTopic(domain, slug);
        showToast(`Unpinned ${slug}`, 'info');
        await refreshTopicsAndPins();
      } catch (err) {
        showToast(err.message, 'danger');
      }
    });
  });
}

// Toggle Pin Helper
async function togglePinTopic(domain, slug) {
  const isPinned = Store.state.pinnedTopics.some(p => (p.topic_id === slug || p.topic_slug === slug));
  try {
    if (isPinned) {
      await API.unpinTopic(domain, slug);
      showToast(`Unpinned ${slug}`, 'info');
    } else {
      await API.pinTopic(domain, slug, 'high');
      showToast(`Pinned ${slug}`, 'success');
    }
    await refreshTopicsAndPins();
  } catch (err) {
    showToast(err.message, 'danger');
  }
}

// =============================================================================
// MICRO-SYNTAX HIGHLIGHTER (Vanilla ES Module, Zero-CDN)
// =============================================================================
const MicroHighlighter = {
  escape(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  },

  languages: {
    python: {
      regex: /(#.*$)|("""[\s\S]*?"""|'''[\s\S]*?''')|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(\b0x[0-9a-fA-F]+\b|\b\d+(?:\.\d+)?\b)|(\b[a-zA-Z_][a-zA-Z0-9_]*\b)|(\s+)|([^a-zA-Z0-9_\s#"']+)/gm,
      keywords: new Set([
        'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue',
        'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from',
        'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not',
        'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
        'True', 'False', 'None', 'self', 'cls'
      ]),
      types: new Set([
        'int', 'float', 'str', 'bool', 'bytes', 'list', 'dict', 'set', 'tuple',
        'object', 'type', 'Any', 'Union', 'Optional', 'List', 'Dict', 'Set',
        'Tuple', 'Callable', 'Protocol', 'TypeVar', 'Generic'
      ])
    },
    go: {
      regex: /(\/\/.*$|\/\*[\s\S]*?\*\/)|(`[^`]*`|"(?:\\.|[^"\\])*")|(\b0x[0-9a-fA-F]+\b|\b\d+(?:\.\d+)?\b)|(\b[a-zA-Z_][a-zA-Z0-9_]*\b)|(\s+)|([^a-zA-Z0-9_\s"'`\/]+|\/[^\/\*])/gm,
      keywords: new Set([
        'break', 'case', 'chan', 'const', 'continue', 'default', 'defer',
        'else', 'fallthrough', 'for', 'func', 'go', 'goto', 'if', 'import',
        'interface', 'map', 'package', 'range', 'return', 'select', 'struct',
        'switch', 'type', 'var', 'true', 'false', 'nil', 'iota'
      ]),
      types: new Set([
        'bool', 'byte', 'complex64', 'complex128', 'error', 'float32', 'float64',
        'int', 'int8', 'int16', 'int32', 'int64', 'rune', 'string', 'uint',
        'uint8', 'uint16', 'uint32', 'uint64', 'uintptr', 'any'
      ])
    },
    rust: {
      regex: /(\/\/.*$|\/\*[\s\S]*?\*\/)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])')|(\b0x[0-9a-fA-F]+\b|\b\d+(?:\.\d+)?\b)|(\b[a-zA-Z_][a-zA-Z0-9_]*\b)|(\s+)|([^a-zA-Z0-9_\s"'/]+|\/[^\/\*])/gm,
      keywords: new Set([
        'as', 'async', 'await', 'break', 'const', 'continue', 'crate', 'dyn',
        'else', 'enum', 'extern', 'false', 'fn', 'for', 'if', 'impl', 'in',
        'let', 'loop', 'match', 'mod', 'move', 'mut', 'pub', 'ref', 'return',
        'self', 'Self', 'static', 'struct', 'super', 'trait', 'true', 'type',
        'unsafe', 'use', 'where', 'while'
      ]),
      types: new Set([
        'bool', 'char', 'i8', 'i16', 'i32', 'i64', 'i128', 'isize',
        'u8', 'u16', 'u32', 'u64', 'u128', 'usize', 'f32', 'f64',
        'str', 'String', 'Option', 'Some', 'None', 'Result', 'Ok', 'Err',
        'Vec', 'Box', 'Rc', 'Arc', 'Mutex'
      ])
    },
    yaml: {
      regex: /(#.*$)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(\b0x[0-9a-fA-F]+\b|\b\d+(?:\.\d+)?\b)|(\b[a-zA-Z0-9_-]+\b(?=\s*:))|(\b[a-zA-Z_][a-zA-Z0-9_]*\b)|(\s+)|([^a-zA-Z0-9_\s#"']+)/gm,
      keywords: new Set([
        'true', 'false', 'yes', 'no', 'on', 'off', 'null', '~',
        'TRUE', 'FALSE', 'YES', 'NO', 'ON', 'OFF', 'NULL'
      ]),
      types: new Set([
        '!!str', '!!int', '!!float', '!!bool', '!!map', '!!seq', '!!null'
      ])
    }
  },

  highlight(code, lang = 'python') {
    const norm = (lang || 'python').toLowerCase().trim();
    const l = norm === 'py' ? 'python' : (norm === 'golang' ? 'go' : (norm === 'rs' ? 'rust' : (norm === 'yml' ? 'yaml' : norm)));
    const config = this.languages[l] || this.languages['python'];
    const re = new RegExp(config.regex.source, 'gm');
    let out = '';
    let m;
    while ((m = re.exec(code)) !== null) {
      const [full, comment, str, num, identOrKey, ident, ws, punct] = m;
      if (comment) out += `<span class="tok-comment">${this.escape(comment)}</span>`;
      else if (str) out += `<span class="tok-string">${this.escape(str)}</span>`;
      else if (num) out += `<span class="tok-number">${this.escape(num)}</span>`;
      else if (l === 'yaml' && identOrKey) {
        out += `<span class="tok-key">${this.escape(identOrKey)}</span>`;
      } else if (ident || identOrKey) {
        const id = ident || identOrKey;
        if (config.keywords.has(id)) out += `<span class="tok-keyword">${this.escape(id)}</span>`;
        else if (config.types.has(id)) out += `<span class="tok-type">${this.escape(id)}</span>`;
        else out += this.escape(id);
      } else if (ws) out += ws;
      else if (punct) out += `<span class="tok-punct">${this.escape(punct)}</span>`;
      else out += this.escape(full);
    }
    return out;
  },

  renderMarkdownWithHighlighting(markdown, defaultLang = 'python') {
    if (!markdown) return '';
    const parts = [];
    let lastIndex = 0;
    const fenceRe = /```([a-zA-Z0-9_-]+)?\n([\s\S]*?)```/g;
    let match;
    while ((match = fenceRe.exec(markdown)) !== null) {
      const textBefore = markdown.slice(lastIndex, match.index);
      const fenceLang = match[1] || defaultLang;
      const code = match[2];
      parts.push(this.formatMarkdownText(textBefore));
      parts.push(`<pre class="code-pre language-${fenceLang}"><code>${this.highlight(code, fenceLang)}</code></pre>`);
      lastIndex = fenceRe.lastIndex;
    }
    parts.push(this.formatMarkdownText(markdown.slice(lastIndex)));
    return parts.join('');
  },

  formatMarkdownText(text) {
    if (!text) return '';
    return this.escape(text)
      .replace(/^### (.*$)/gim, '<h4 style="margin:8px 0 4px;font-size:14px;font-weight:600;">$1</h4>')
      .replace(/^## (.*$)/gim, '<h3 style="margin:12px 0 6px;font-size:16px;font-weight:700;">$1</h3>')
      .replace(/^# (.*$)/gim, '<h2 style="margin:14px 0 8px;font-size:18px;font-weight:700;">$1</h2>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
      .replace(/\n/g, '<br>');
  },

  renderToElement(element, content, defaultLang = 'python') {
    if (!element) return;
    if (content && content.includes('```')) {
      element.innerHTML = this.renderMarkdownWithHighlighting(content, defaultLang);
    } else {
      element.innerHTML = `<pre class="code-pre language-${defaultLang}"><code>${this.highlight(content || '', defaultLang)}</code></pre>`;
    }
  }
};

// Load and Render Topic Detail
async function loadTopicDetail(domain, topicSlug) {
  showView('topic-detail');
  document.getElementById('breadcrumb-domain').textContent = domain;
  document.getElementById('breadcrumb-topic').textContent = topicSlug;
  document.getElementById('topic-detail-title').textContent = topicSlug.replace(/-/g, ' ').toUpperCase();

  try {
    const detail = await API.getTopicDetail(domain, topicSlug);
    Store.setState({ activeTopicDetail: detail });

    // Fundamentals
    MicroHighlighter.renderToElement(document.getElementById('topic-fundamentals-content'), detail.fundamentals || 'No fundamentals documented.', 'python');
    // Rubric
    MicroHighlighter.renderToElement(document.getElementById('topic-rubric-content'), detail.rubric || 'No rubric documented.', 'yaml');

    // References
    const refContainer = document.getElementById('topic-references-content');
    if (Array.isArray(detail.references) && detail.references.length > 0) {
      refContainer.innerHTML = detail.references.map(r => `
        <div style="margin-bottom:var(--space-md); padding-bottom:var(--space-sm); border-bottom:1px solid var(--border-light);">
          <div style="font-weight:700; font-size:14px;">${r.title || r.name || 'Reference Document'}</div>
          <div style="font-size:12px; color:var(--text-secondary); margin-top:2px;">
            ${r.author || r.institution || ''} ${r.year ? `(${r.year})` : ''}
          </div>
          ${r.url ? `<a href="${r.url}" target="_blank" style="font-size:11px; color:var(--accent-primary); word-break:break-all;">${r.url}</a>` : ''}
        </div>
      `).join('');
    } else {
      refContainer.innerHTML = '<p style="color:var(--text-muted);">No references found for this topic.</p>';
    }

    // Exercises Grid
    const exContainer = document.getElementById('topic-exercises-grid');
    if (Array.isArray(detail.exercises) && detail.exercises.length > 0) {
      exContainer.innerHTML = detail.exercises.map(ex => `
        <div class="domain-card">
          <div class="domain-card-header">
            <span style="font-weight:700; font-size:13px;">${ex.title || ex.exercise_id}</span>
            <span class="badge badge-l5">${ex.exercise_id}</span>
          </div>
          <p style="font-size:12px; color:var(--text-secondary); margin-bottom:var(--space-md);">
            ${ex.content.slice(0, 150)}...
          </p>
          <button class="btn btn-primary btn-sm btn-launch-quiz" data-topic="${topicSlug}" data-tier="${ex.exercise_id}">Practice This Tier</button>
        </div>
      `).join('');

      exContainer.querySelectorAll('.btn-launch-quiz').forEach(btn => {
        btn.addEventListener('click', () => {
          const t = btn.dataset.topic;
          const tier = btn.dataset.tier;
          location.hash = `#quiz/${t}/${tier}`;
        });
      });
    } else {
      exContainer.innerHTML = '<p style="color:var(--text-muted);">No tiered exercises found.</p>';
    }

    // Update Action Buttons
    const isPinned = detail.pinned;
    const pinBtn = document.getElementById('btn-pin-topic');
    pinBtn.textContent = isPinned ? 'Unpin Topic' : 'Pin Topic (p)';
    pinBtn.onclick = async () => {
      await togglePinTopic(domain, topicSlug);
      loadTopicDetail(domain, topicSlug);
    };

    document.getElementById('btn-start-quiz-from-topic').onclick = () => {
      location.hash = `#quiz/${topicSlug}/starter`;
    };

    document.getElementById('btn-start-interview-from-topic').onclick = () => {
      location.hash = `#interview/${topicSlug}`;
    };

    document.getElementById('btn-capture-from-topic').onclick = () => {
      openDurableCaptureModal(domain, topicSlug);
    };

  } catch (err) {
    showToast(`Error loading topic: ${err.message}`, 'danger');
  }
}

// Quiz Controller
async function startQuizSession(topicSlug, initialTier = 'starter') {
  showView('quiz');
  document.getElementById('quiz-topic-badge').textContent = topicSlug;
  document.getElementById('quiz-tier-badge').textContent = initialTier.toUpperCase();
  document.getElementById('quiz-feedback-drawer').style.display = 'none';

  try {
    const sessionData = await API.startQuiz(topicSlug, initialTier);
    Store.setState({ activeQuizSession: sessionData });
    MicroHighlighter.renderToElement(document.getElementById('quiz-problem-prompt'), sessionData.prompt, 'python');

    const ratings = await API.getRatings();
    const currentRating = ratings.ratings?.[topicSlug] || 3.0;
    document.getElementById('quiz-rating-display').textContent = currentRating.toFixed(2);
  } catch (err) {
    showToast(`Error starting quiz: ${err.message}`, 'danger');
  }
}

async function submitQuizAnswer() {
  const session = Store.state.activeQuizSession;
  if (!session) {
    showToast('No active quiz session found.', 'warning');
    return;
  }
  const answer = document.getElementById('quiz-code-editor').value;
  try {
    const res = await API.submitQuizTurn({
      session_id: session.session_id,
      exercise_id: session.exercise_id,
      topic_slug: session.topic_id,
      user_response: answer,
    });

    const drawer = document.getElementById('quiz-feedback-drawer');
    drawer.style.display = 'block';
    const passClass = res.passed ? 'badge-pass' : 'badge-miss';
    const statusText = res.passed ? 'PASSED — Advancing Ladder' : 'SCAFFOLD TURN — Missed Invariant';

    drawer.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-sm);">
        <span class="badge ${passClass}">${statusText}</span>
        <span style="font-family:var(--font-mono); font-size:12px;">New Rating: <strong>${res.new_rating.toFixed(2)}</strong></span>
      </div>
      <p style="font-size:13px; margin-bottom:var(--space-md);">${res.feedback || res.evaluation}</p>
      <div style="display:flex; gap:var(--space-sm);">
        <button id="btn-quiz-next-exercise" class="btn btn-primary btn-sm">Next Problem (${res.next_difficulty_level})</button>
        <button id="btn-quiz-durable-capture" class="btn btn-secondary btn-sm">Capture as Durable Learning (d)</button>
      </div>
    `;

    document.getElementById('quiz-rating-display').textContent = res.new_rating.toFixed(2);

    document.getElementById('btn-quiz-next-exercise')?.addEventListener('click', () => {
      Store.setState({
        activeQuizSession: {
          session_id: res.session_id,
          exercise_id: res.next_exercise.exercise_id,
          topic_id: session.topic_id,
          prompt: res.next_exercise.prompt,
        }
      });
      MicroHighlighter.renderToElement(document.getElementById('quiz-problem-prompt'), res.next_exercise.prompt, 'python');
      document.getElementById('quiz-tier-badge').textContent = res.next_difficulty_level.toUpperCase();
      document.getElementById('quiz-code-editor').value = '';
      drawer.style.display = 'none';
    });

    document.getElementById('btn-quiz-durable-capture')?.addEventListener('click', () => {
      openDurableCaptureModal('general', session.topic_id);
    });

    await refreshTopicsAndPins();
  } catch (err) {
    showToast(`Submission failed: ${err.message}`, 'danger');
  }
}

// =============================================================================
// INTERVIEW CONTROLLER (WebSocket Stream with REST Fallback)
// =============================================================================
let interviewTimerInterval = null;
let interviewSecondsRemaining = 45 * 60;
let interviewWebSocket = null;
let activeStreamingMessageEl = null;

function setInterviewWsStatus(text, className) {
  const statusEl = document.getElementById('interview-ws-status');
  if (statusEl) {
    statusEl.textContent = text;
    statusEl.className = className || '';
  }
}

function connectInterviewWebSocket(sessionId) {
  if (interviewWebSocket) {
    try { interviewWebSocket.close(); } catch (e) {}
    interviewWebSocket = null;
  }

  setInterviewWsStatus('● Connecting WS...', 'ws-connecting');

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  const token = Store.state.apiToken;
  const tokenQuery = token ? `?token=${encodeURIComponent(token)}` : '';
  const wsUrl = `${protocol}//${host}/api/interview/${sessionId}/stream${tokenQuery}`;

  try {
    const ws = new WebSocket(wsUrl);
    interviewWebSocket = ws;

    ws.onopen = () => {
      if (ws !== interviewWebSocket) return;
      setInterviewWsStatus('● WebSocket Active', 'ws-active');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      } catch (err) {
        console.error('Failed to parse WebSocket message frame:', err);
      }
    };

    ws.onerror = (err) => {
      console.warn('WebSocket stream encountered error; operating in REST fallback mode.', err);
      setInterviewWsStatus('○ REST Fallback', 'ws-fallback');
    };

    ws.onclose = () => {
      if (ws === interviewWebSocket) {
        setInterviewWsStatus('○ REST Fallback', 'ws-fallback');
        interviewWebSocket = null;
      }
    };
  } catch (err) {
    console.warn('WebSocket instantiation failed, defaulting to REST:', err);
    setInterviewWsStatus('○ REST Fallback', 'ws-fallback');
  }
}

function handleWebSocketMessage(data) {
  if (data.type === 'chunk') {
    if (activeStreamingMessageEl) {
      const content = activeStreamingMessageEl.querySelector('.stream-content');
      if (content) {
        content.textContent += data.delta;
      }
      const feed = document.getElementById('interview-chat-feed');
      if (feed) feed.scrollTop = feed.scrollHeight;
    }
  } else if (data.type === 'done') {
    if (activeStreamingMessageEl) {
      const content = activeStreamingMessageEl.querySelector('.stream-content');
      if (content && data.interviewer_message) {
        content.textContent = data.interviewer_message;
      }
      const cursor = activeStreamingMessageEl.querySelector('.typing-cursor');
      if (cursor) cursor.remove();
      activeStreamingMessageEl = null;
    }
    updateInterviewPhase(data.current_phase);
    updateHintsBudget(data.hints_remaining);
    setTurnInputEnabled(true);
  } else if (data.type === 'error') {
    showToast(data.message || 'Stream error', 'danger');
    if (activeStreamingMessageEl) {
      activeStreamingMessageEl.remove();
      activeStreamingMessageEl = null;
    }
    setTurnInputEnabled(true);
  }
}

function setTurnInputEnabled(enabled) {
  const input = document.getElementById('interview-turn-input');
  const btnSend = document.getElementById('btn-send-interview-turn');
  if (input) input.disabled = !enabled;
  if (btnSend) btnSend.disabled = !enabled;
}

async function startInterviewSession(topicSlug, roleTrack = 'faang_swe_l5_l6', targetCompany = 'Google') {
  showView('interview');
  document.getElementById('interview-company-badge').textContent = targetCompany;
  document.getElementById('interview-track-badge').textContent = roleTrack;
  const feed = document.getElementById('interview-chat-feed');
  feed.innerHTML = '';

  try {
    const sessionData = await API.startInterview({
      topic: topicSlug,
      role_track: roleTrack,
      target_company: targetCompany,
      mode: 'hints',
      time_limit_minutes: 45,
    });
    Store.setState({ activeInterviewSession: sessionData });

    // Render welcome message
    appendChatMessage('interviewer', sessionData.interviewer_message);
    updateInterviewPhase(sessionData.current_phase);
    updateHintsBudget(sessionData.hints_remaining);

    // Establish authentic WebSocket streaming connection
    connectInterviewWebSocket(sessionData.session_id);

    // Start timer countdown
    clearInterval(interviewTimerInterval);
    interviewSecondsRemaining = 45 * 60;
    interviewTimerInterval = setInterval(() => {
      interviewSecondsRemaining--;
      if (interviewSecondsRemaining <= 0) {
        clearInterval(interviewTimerInterval);
        showToast('Time is up for this interview round!', 'warning');
      }
      const mins = Math.floor(interviewSecondsRemaining / 60);
      const secs = interviewSecondsRemaining % 60;
      document.getElementById('interview-timer').textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }, 1000);

  } catch (err) {
    showToast(`Failed to start interview: ${err.message}`, 'danger');
  }
}

function appendChatMessage(speaker, text) {
  const feed = document.getElementById('interview-chat-feed');
  if (!feed) return;
  const msg = document.createElement('div');
  msg.className = `chat-msg ${speaker}`;
  msg.textContent = text;
  feed.appendChild(msg);
  feed.scrollTop = feed.scrollHeight;
}

function updateInterviewPhase(phase) {
  document.querySelectorAll('.phase-step').forEach(step => {
    step.classList.remove('active');
    if (step.dataset.phase === phase) {
      step.classList.add('active');
    }
  });
}

function updateHintsBudget(remaining) {
  const btn = document.getElementById('btn-request-hint');
  if (btn) {
    btn.textContent = `Hint (h) [${remaining} left]`;
    btn.disabled = remaining <= 0;
  }
}

async function sendInterviewTurn(turnType = 'candidate_dialog', customMessage = null) {
  const session = Store.state.activeInterviewSession;
  if (!session) return;
  const input = document.getElementById('interview-turn-input');
  const message = customMessage || input.value.trim();
  if (!message && turnType !== 'request_hint') return;

  if (turnType !== 'request_hint') {
    appendChatMessage('candidate', message);
    input.value = '';
  }

  // Attempt WebSocket stream if socket is OPEN
  if (interviewWebSocket && interviewWebSocket.readyState === WebSocket.OPEN) {
    try {
      const feed = document.getElementById('interview-chat-feed');
      const msg = document.createElement('div');
      msg.className = `chat-msg ${turnType === 'request_hint' ? 'hint' : 'interviewer'}`;

      const contentSpan = document.createElement('span');
      contentSpan.className = 'stream-content';
      const cursorSpan = document.createElement('span');
      cursorSpan.className = 'typing-cursor';

      msg.appendChild(contentSpan);
      msg.appendChild(cursorSpan);
      feed.appendChild(msg);
      feed.scrollTop = feed.scrollHeight;
      activeStreamingMessageEl = msg;

      setTurnInputEnabled(false);
      interviewWebSocket.send(JSON.stringify({
        message: message,
        turn_type: turnType,
      }));
      return;
    } catch (wsErr) {
      console.warn('WS send failed; falling back to REST:', wsErr);
      if (activeStreamingMessageEl) {
        activeStreamingMessageEl.remove();
        activeStreamingMessageEl = null;
      }
    }
  }

  // Graceful REST Fallback
  try {
    setTurnInputEnabled(false);
    const res = await API.submitInterviewTurn(session.session_id, {
      user_response: message,
      turn_type: turnType,
    });
    appendChatMessage(turnType === 'request_hint' ? 'hint' : 'interviewer', res.interviewer_message);
    updateInterviewPhase(res.current_phase);
    updateHintsBudget(res.hints_remaining);
  } catch (err) {
    showToast(`Turn failed: ${err.message}`, 'danger');
  } finally {
    setTurnInputEnabled(true);
  }
}

async function finalizeInterview() {
  const session = Store.state.activeInterviewSession;
  if (!session) return;
  try {
    if (interviewWebSocket) {
      try { interviewWebSocket.close(); } catch (e) {}
      interviewWebSocket = null;
    }
    const scorecard = await API.getScorecard(session.session_id);
    clearInterval(interviewTimerInterval);
    openScorecardModal(scorecard);
    await refreshTopicsAndPins();
  } catch (err) {
    showToast(`Failed to finalize interview: ${err.message}`, 'danger');
  }
}


function openScorecardModal(card) {
  const modal = document.getElementById('modal-scorecard');
  const content = document.getElementById('scorecard-modal-content');
  if (!modal || !content) return;

  const radarSvg = SVGRenderer.renderRadarChart(card.rubric_scores, 240);

  content.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-md); flex-wrap:wrap; gap:var(--space-sm);">
      <div>
        <span class="badge ${card.overall_score >= 3.5 ? 'badge-pass' : 'badge-miss'}" style="font-size:14px; padding:4px 10px;">
          ${card.bar_decision}
        </span>
        <span style="font-size:13px; font-weight:600; margin-left:var(--space-sm);">${card.level_calibration} Calibration</span>
      </div>
      <div style="font-family:var(--font-mono); font-size:14px;">
        Overall Score: <strong>${card.overall_score.toFixed(2)}</strong> / 5.00
      </div>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:var(--space-md); align-items:center;">
      <div style="display:flex; justify-content:center;">
        ${radarSvg}
      </div>
      <div>
        <div style="font-size:12px; margin-bottom:var(--space-xs);"><strong>Decomposition:</strong> ${card.rubric_scores.decomposition}/5.0</div>
        <div style="font-size:12px; margin-bottom:var(--space-xs);"><strong>Execution:</strong> ${card.rubric_scores.execution}/5.0</div>
        <div style="font-size:12px; margin-bottom:var(--space-xs);"><strong>Architecture:</strong> ${card.rubric_scores.architecture}/5.0</div>
        <div style="font-size:12px; margin-bottom:var(--space-xs);"><strong>Resilience:</strong> ${card.rubric_scores.resilience}/5.0</div>
        <div style="font-size:12px; margin-bottom:var(--space-xs);"><strong>Communication:</strong> ${card.rubric_scores.communication}/5.0</div>
      </div>
    </div>

    <div style="margin-top:var(--space-md); padding:var(--space-md); background:var(--bg-tertiary); border-radius:var(--radius-md);">
      <div style="font-weight:700; font-size:12px; margin-bottom:4px;">Evaluator Feedback:</div>
      <p style="font-size:12px; color:var(--text-secondary);">${card.feedback}</p>
    </div>
  `;

  modal.showModal();
}

// Role Alignment Controller
async function runRoleAlignment() {
  const roleTrack = document.getElementById('align-role-track').value;
  const company = document.getElementById('align-target-company').value;
  const jdText = document.getElementById('align-jd-text').value.trim();
  const resumeText = document.getElementById('align-resume-text').value.trim();

  if (!jdText) {
    showToast('Please provide a job description.', 'warning');
    return;
  }

  try {
    const res = await API.analyzeResumeFit({
      role_track: roleTrack,
      target_company: company,
      job_description_text: jdText,
      resume_text: resumeText || null,
    });

    const container = document.getElementById('alignment-results-container');
    container.style.display = 'block';

    const gaugeSvg = SVGRenderer.renderFitGauge(Math.round(res.fit_score_percentage), 160);

    container.innerHTML = `
      <div style="background:var(--bg-card); border:1px solid var(--border-light); border-radius:var(--radius-lg); padding:var(--space-lg); margin-bottom:var(--space-lg);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:var(--space-md);">
          <div>
            <h3 style="font-size:18px; font-weight:700;">Role Fit Score</h3>
            <p style="font-size:13px; color:var(--text-secondary);">Calibrated to ${res.target_company} ${res.target_level}</p>
          </div>
          <div>
            ${gaugeSvg}
          </div>
        </div>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:var(--space-lg);">
        <div style="background:var(--bg-card); border:1px solid var(--border-light); border-radius:var(--radius-lg); padding:var(--space-md);">
          <h4 style="font-size:14px; font-weight:700; margin-bottom:var(--space-md);">High-Leverage Gaps</h4>
          ${(res.high_leverage_gaps || []).map(g => `
            <div style="margin-bottom:var(--space-sm); padding:var(--space-sm); background:var(--bg-tertiary); border-radius:var(--radius-md);">
              <div style="display:flex; justify-content:space-between;">
                <strong>${g.topic_id}</strong>
                <span class="badge ${g.priority === 'critical' ? 'badge-miss' : 'badge-l5'}">${g.priority}</span>
              </div>
              <div style="font-size:12px; color:var(--text-secondary); margin-top:2px;">${g.reason}</div>
            </div>
          `).join('')}
        </div>

        <div style="background:var(--bg-card); border:1px solid var(--border-light); border-radius:var(--radius-lg); padding:var(--space-md);">
          <h4 style="font-size:14px; font-weight:700; margin-bottom:var(--space-md);">Custom 5-Round Interview Loop</h4>
          ${(res.custom_interview_loop || []).map(r => `
            <div style="margin-bottom:var(--space-xs); font-size:13px; padding:var(--space-xs) 0; border-bottom:1px solid var(--border-light);">
              <strong>Round ${r.round}:</strong> ${r.topic} (${r.type || 'evaluation'})
            </div>
          `).join('')}
        </div>
      </div>
    `;

    showToast('Alignment analysis completed.', 'success');
  } catch (err) {
    showToast(`Alignment analysis failed: ${err.message}`, 'danger');
  }
}

// Telemetry Controller
async function loadTelemetry() {
  showView('telemetry');
  try {
    const summary = await API.getTelemetrySummary();
    document.getElementById('telem-total-requests').textContent = summary.total_requests || 0;
    document.getElementById('telem-total-tokens').textContent = (summary.total_tokens || 0).toLocaleString();
    document.getElementById('telem-actual-cost').textContent = `$${(summary.total_estimated_cost_usd || 0.0).toFixed(2)}`;
    document.getElementById('telem-nominal-value').textContent = `$${(summary.total_nominal_value_usd || 0.0).toFixed(2)}`;

    const tbody = document.getElementById('telemetry-table-body');
    if (summary.recent_events && summary.recent_events.length > 0) {
      tbody.innerHTML = summary.recent_events.slice().reverse().map(ev => `
        <tr>
          <td style="font-family:var(--font-mono); font-size:11px;">${ev.timestamp?.slice(11, 19) || ''}</td>
          <td><span class="badge badge-company">${ev.provider}</span></td>
          <td style="font-family:var(--font-mono); font-size:11px;">${ev.model}</td>
          <td><span class="badge badge-l4">${ev.execution_tier || 'tier1'}</span></td>
          <td style="font-family:var(--font-mono); font-size:11px;">${(ev.input_tokens || 0) + (ev.output_tokens || 0)}</td>
          <td><span class="badge ${ev.success ? 'badge-pass' : 'badge-miss'}">${ev.success ? 'PASS' : 'FAIL'}</span></td>
        </tr>
      `).join('');
    } else {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:20px;">No telemetry records yet.</td></tr>';
    }
  } catch (err) {
    showToast(`Failed to load telemetry: ${err.message}`, 'danger');
  }
}

// Durable Capture Modal Handler
function openDurableCaptureModal(domain = 'leetcode', topicSlug = 'algorithms') {
  const modal = document.getElementById('modal-durable-capture');
  if (!modal) return;
  document.getElementById('capture-select-domain').value = domain;
  document.getElementById('capture-input-topic').value = topicSlug;
  modal.showModal();
}

async function handleDurableCaptureSubmit(e) {
  e.preventDefault();
  const title = document.getElementById('capture-input-title').value.trim();
  const domain = document.getElementById('capture-select-domain').value;
  const topicSlug = document.getElementById('capture-input-topic').value.trim();
  const mentalModel = document.getElementById('capture-input-model').value.trim();
  const invariantsStr = document.getElementById('capture-input-invariants').value.trim();
  const code = document.getElementById('capture-input-code').value.trim();

  const invariants = invariantsStr ? invariantsStr.split(',').map(s => s.trim()).filter(Boolean) : [];

  try {
    const res = await API.recordDurableLearning(domain, topicSlug, {
      title,
      mental_model: mentalModel,
      invariants,
      code_examples: code,
    });
    showToast(`Durable learning committed: ${res.file_path}`, 'success');
    document.getElementById('modal-durable-capture').close();
    document.getElementById('form-durable-capture').reset();
  } catch (err) {
    showToast(`Failed to record learning: ${err.message}`, 'danger');
  }
}

// Refresh Data
async function refreshTopicsAndPins() {
  try {
    const [topicRes, pinRes, ratingsRes] = await Promise.all([
      API.listTopics(),
      API.getPinnedTopics(),
      API.getRatings(),
    ]);

    Store.setState({
      topics: topicRes.topics || [],
      pinnedTopics: pinRes.pinned_topics || [],
      userRatings: ratingsRes.ratings || {},
    });

    renderDashboard();
    renderPinnedBar();
  } catch (err) {
    console.error('Refresh error:', err);
  }
}

// =============================================================================
// 6. ROUTER & GLOBAL SHORTCUTS
// =============================================================================
function handleHashRoute() {
  const hash = location.hash.replace(/^#/, '') || 'dashboard';
  const parts = hash.split('/');
  const route = parts[0];

  if (route === 'dashboard') {
    showView('dashboard');
  } else if (route === 'topic' && parts.length >= 3) {
    loadTopicDetail(parts[1], parts[2]);
  } else if (route === 'quiz') {
    const topic = parts[1] || 'algorithms';
    const tier = parts[2] || 'starter';
    startQuizSession(topic, tier);
  } else if (route === 'interview') {
    const topic = parts[1] || 'algorithms';
    startInterviewSession(topic);
  } else if (route === 'alignment') {
    showView('alignment');
  } else if (route === 'telemetry') {
    loadTelemetry();
  } else {
    showView('dashboard');
  }
}

function setupGlobalShortcuts() {
  window.addEventListener('keydown', (e) => {
    // If active in an input/textarea, only intercept Ctrl+Enter and Esc
    const isEditing = ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName);

    if (e.key === 'Escape') {
      document.querySelectorAll('dialog[open]').forEach(d => d.close());
      return;
    }

    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault();
      if (Store.state.activeView === 'quiz') {
        submitQuizAnswer();
      } else if (Store.state.activeView === 'interview') {
        sendInterviewTurn();
      }
      return;
    }

    if (isEditing) return;

    if (e.key === '/') {
      e.preventDefault();
      document.getElementById('modal-search')?.showModal();
    } else if (e.key === '?') {
      e.preventDefault();
      document.getElementById('modal-shortcuts')?.showModal();
    } else if (e.key === 'd') {
      e.preventDefault();
      openDurableCaptureModal();
    } else if (e.key === 'h' && Store.state.activeView === 'interview') {
      e.preventDefault();
      sendInterviewTurn('request_hint');
    } else if (e.key === 'j') {
      // Table down
      const maxIdx = Store.state.topics.length - 1;
      const nextIdx = Math.min(maxIdx, Store.state.selectedTopicIndex + 1);
      Store.setState({ selectedTopicIndex: nextIdx });
      renderDashboard();
    } else if (e.key === 'k') {
      // Table up
      const prevIdx = Math.max(0, Store.state.selectedTopicIndex - 1);
      Store.setState({ selectedTopicIndex: prevIdx });
      renderDashboard();
    } else if (e.key === 'Enter' && Store.state.activeView === 'dashboard') {
      const topic = Store.state.topics[Store.state.selectedTopicIndex];
      if (topic) {
        location.hash = `#topic/${topic.domain}/${topic.slug}`;
      }
    } else if (e.key === 'p' && Store.state.activeView === 'dashboard') {
      const topic = Store.state.topics[Store.state.selectedTopicIndex];
      if (topic) {
        togglePinTopic(topic.domain, topic.slug);
      }
    }
  });
}

// =============================================================================
// 7. INITIALIZATION & BOOTSTRAP
// =============================================================================
async function initApp() {
  // Theme init
  Store.setTheme(Store.state.theme);
  document.getElementById('btn-theme-toggle')?.addEventListener('click', () => {
    Store.setTheme(Store.state.theme === 'light' ? 'dark' : 'light');
  });

  // Modal dismiss buttons
  document.querySelectorAll('.modal-close-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.closest('dialog')?.close();
    });
  });

  // Header quick buttons
  document.getElementById('btn-global-search')?.addEventListener('click', () => {
    document.getElementById('modal-search')?.showModal();
  });
  document.getElementById('btn-shortcuts')?.addEventListener('click', () => {
    document.getElementById('modal-shortcuts')?.showModal();
  });
  document.getElementById('btn-auth')?.addEventListener('click', () => {
    document.getElementById('modal-auth')?.showModal();
  });

  // Auth form
  document.getElementById('form-auth-token')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const token = document.getElementById('auth-token-input').value.trim();
    Store.setApiToken(token);
    document.getElementById('modal-auth').close();
    showToast('Token saved.', 'success');
  });

  // Deep dive tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const targetPane = document.getElementById(btn.dataset.tab);
      if (targetPane) targetPane.classList.add('active');
    });
  });

  // Filter buttons on dashboard
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const domain = btn.dataset.filter;
      const res = await API.listTopics(domain);
      Store.setState({ topics: res.topics || [] });
      renderDashboard();
    });
  });

  // Search input filter
  document.getElementById('topic-search-input')?.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase();
    const filtered = Store.state.topics.filter(t => t.slug.includes(q) || t.title.toLowerCase().includes(q));
    const tbody = document.getElementById('topic-table-body');
    if (tbody) {
      tbody.querySelectorAll('.topic-row').forEach(row => {
        const slug = row.dataset.slug.toLowerCase();
        row.style.display = slug.includes(q) ? '' : 'none';
      });
    }
  });

  // Actions in Quiz & Interview
  document.getElementById('btn-quiz-submit')?.addEventListener('click', submitQuizAnswer);
  document.getElementById('btn-send-interview-turn')?.addEventListener('click', () => sendInterviewTurn());
  document.getElementById('btn-request-hint')?.addEventListener('click', () => sendInterviewTurn('request_hint'));
  document.getElementById('btn-finalize-interview')?.addEventListener('click', finalizeInterview);
  document.getElementById('btn-run-alignment')?.addEventListener('click', runRoleAlignment);
  document.getElementById('form-durable-capture')?.addEventListener('submit', handleDurableCaptureSubmit);

  // Status check and pill update
  try {
    await API.checkStatus();
    const statusText = document.getElementById('connection-text');
    const statusDot = document.getElementById('connection-dot');
    if (Store.state.connectionStatus === 'connected_local') {
      statusText.textContent = 'Local:8795';
      statusDot.className = 'status-dot';
    } else if (Store.state.connectionStatus === 'connected_tailnet') {
      statusText.textContent = 'Tailnet (100.64.162.123)';
      statusDot.className = 'status-dot';
    }
  } catch (e) {
    console.warn('Status check warning:', e);
  }

  // Load initial topics and pins
  await refreshTopicsAndPins();

  // Router setup
  window.addEventListener('hashchange', handleHashRoute);
  handleHashRoute();

  // Global keyboard shortcuts
  setupGlobalShortcuts();
}

// Start
document.addEventListener('DOMContentLoaded', initApp);
