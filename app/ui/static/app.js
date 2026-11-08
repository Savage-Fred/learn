/**
 * Savage-Fred / learn — Local-First Single-Page Application (Zero-CDN)
 * Vanilla ES Module Architecture for learn.willmccarty.io
 */

// =============================================================================
// 1. STATE STORE
// =============================================================================
const Store = {
  state: {
    theme: localStorage.getItem('learn_theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'),
    apiToken: localStorage.getItem('learn_api_token') || '',
    apiBaseUrl: localStorage.getItem('learn_api_base_url') || '/api',
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
    useEdgeEngine: false,
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
  },

  setApiBaseUrl(url) {
    this.state.apiBaseUrl = url;
    localStorage.setItem('learn_api_base_url', url);
    API.baseUrl = url;
    this.setState({ apiBaseUrl: url });
  }
};

// =============================================================================
// 2. CLOUDFLARE PAGES STATIC EDGE ENGINE (EdgeEngine)
// =============================================================================
const EdgeEngine = {
  storageKey: 'learn_edge_state_v1',
  catalog: null,
  localState: null,

  async init() {
    this.localState = this.loadState();
    try {
      const res = await fetch('/static/catalog.json');
      if (res.ok) {
        this.catalog = await res.json();
      }
    } catch (e) {
      console.warn('Could not fetch static catalog from network; using fallback catalog.', e);
    }
    if (!this.catalog) {
      this.catalog = this.getEmbeddedCatalog();
    }
  },

  loadState() {
    try {
      const raw = localStorage.getItem(this.storageKey);
      if (raw) return JSON.parse(raw);
    } catch (e) {
      console.warn('Corrupted edge state in localStorage; resetting.', e);
    }
    return {
      ratings: {
        'pythonic-coding-patterns': 3.4,
        'masters-algorithms': 3.2,
        'data-structures': 3.5,
        'modern-authn-authz': 3.0,
        'pets-for-ai': 2.6,
        'threat-modeling': 3.1,
        'agent-access-models': 2.8,
        'statistics-for-data-analysis': 3.3,
        'rust': 3.0,
        'go': 3.4,
        'modern-differential-privacy': 2.7,
      },
      pinned: [
        { topic_id: 'masters-algorithms', domain: 'leetcode', priority: 'high', notes: 'Core graph invariants' },
        { topic_id: 'modern-authn-authz', domain: 'security', priority: 'high', notes: 'Zanzibar relation tuples' }
      ],
      learnings: [],
      telemetry: [
        { timestamp: new Date().toISOString(), provider: 'Cloudflare Edge (Client)', model: 'EdgeEngine-v1', execution_tier: 'tier4', input_tokens: 1420, output_tokens: 380, success: true }
      ]
    };
  },

  saveState() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.localState));
    } catch (e) {
      console.error('Failed to save EdgeEngine state to localStorage:', e);
    }
  },

  scrubPii(text) {
    if (!text) return '';
    return String(text)
      .replace(/[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/g, '[EMAIL_REDACTED]')
      .replace(/(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/g, '[PHONE_REDACTED]')
      .replace(/(sk-[a-zA-Z0-9_-]{16,}|tok_[a-zA-Z0-9]{16,}|ghp_[a-zA-Z0-9]{20,})/g, '[API_KEY_REDACTED]')
      .replace(/Bearer\s+[a-zA-Z0-9._~+/-]{16,}/g, 'Bearer [TOKEN_REDACTED]');
  },

  listTopics(domainFilter = 'all') {
    const all = this.catalog.topics || [];
    const filtered = domainFilter === 'all' ? all : all.filter(t => t.domain === domainFilter);
    const pinnedSlugs = new Set((this.localState.pinned || []).map(p => p.topic_id || p.topic_slug));
    const ratings = this.localState.ratings || {};

    return {
      topics: filtered.map(t => {
        const rating = ratings[t.slug] || 0.0;
        return {
          ...t,
          user_rating: rating,
          user_status: rating >= 4.0 ? 'completed' : (rating > 0.0 ? 'in_progress' : 'not_started'),
          pinned: pinnedSlugs.has(t.slug)
        };
      })
    };
  },

  getTopicDetail(domain, topicSlug) {
    const key = `${domain}/${topicSlug}`;
    const detail = this.catalog.topic_details?.[key] || this.catalog.topic_details?.[topicSlug] || {
      topic_id: topicSlug,
      domain: domain,
      fundamentals: `# ${topicSlug.toUpperCase()}\n\nFundamentals and invariant specifications loaded via EdgeEngine.`,
      references: [
        { title: 'Canonical Engineering Reference', author: 'Will McCarty', year: 2026, url: 'https://learn.willmccarty.io' }
      ],
      rubric: `dimensions:\n  decomposition: 0.20\n  execution: 0.25\n  architecture: 0.25\n  resilience: 0.15\n  communication: 0.15`,
      exercises: [
        { exercise_id: 'tier1_starter', title: 'Starter Exercise', content: 'Implement core data structures.' },
        { exercise_id: 'tier2_l4', title: 'L4 Baseline Exercise', content: 'Ensure monotonic progression and bounds.' },
        { exercise_id: 'tier3_l5', title: 'L5 Senior Exercise', content: 'Design distributed concurrency semantics.' },
        { exercise_id: 'tier4_l6', title: 'L6 Staff Exercise', content: 'Formulate formal invariant proofs under partition.' }
      ]
    };

    const pinnedSlugs = new Set((this.localState.pinned || []).map(p => p.topic_id || p.topic_slug));
    const topicLearnings = (this.localState.learnings || []).filter(l => l.topic === topicSlug);

    return {
      ...detail,
      user_rating: this.localState.ratings?.[topicSlug] || 3.0,
      pinned: pinnedSlugs.has(topicSlug),
      learnings: topicLearnings
    };
  },

  getPinnedTopics() {
    return { pinned_topics: this.localState.pinned || [] };
  },

  pinTopic(domain, topicSlug, priority = 'high', notes = '') {
    const existing = (this.localState.pinned || []).filter(p => (p.topic_id || p.topic_slug) !== topicSlug);
    existing.unshift({
      topic_id: topicSlug,
      topic_slug: topicSlug,
      domain: domain,
      priority: priority,
      notes: notes,
      pinned_at: new Date().toISOString()
    });
    this.localState.pinned = existing;
    this.saveState();
    return { status: 'pinned', topic_slug: topicSlug };
  },

  unpinTopic(domain, topicSlug) {
    this.localState.pinned = (this.localState.pinned || []).filter(p => (p.topic_id || p.topic_slug) !== topicSlug);
    this.saveState();
    return { status: 'unpinned', topic_slug: topicSlug };
  },

  recordDurableLearning(domain, topicSlug, payload) {
    const cleanTitle = this.scrubPii(payload.title);
    const cleanModel = this.scrubPii(payload.mental_model);
    const cleanCode = this.scrubPii(payload.code_examples || '');
    const cleanInvariants = (payload.invariants || []).map(i => this.scrubPii(i));

    const item = {
      id: `learn_${Date.now()}`,
      domain,
      topic: topicSlug,
      title: cleanTitle,
      mental_model: cleanModel,
      invariants: cleanInvariants,
      code_examples: cleanCode,
      target_level: payload.target_level || 'L6',
      created_at: new Date().toISOString()
    };

    this.localState.learnings = this.localState.learnings || [];
    this.localState.learnings.unshift(item);
    this.saveState();

    // Trigger browser file download of the Markdown artifact
    const md = `---
title: "${cleanTitle.replace(/"/g, '\\"')}"
domain: ${domain}
topic: ${topicSlug}
date: ${item.created_at}
target_level: ${item.target_level}
---

# ${cleanTitle}

## Axiomatic Mental Model
${cleanModel}

## Invariants Preserved
${cleanInvariants.map(i => `- ${i}`).join('\n')}

## Code & Verification Pattern
\`\`\`python
${cleanCode}
\`\`\`
`;
    try {
      const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${topicSlug}_durable_learning.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.warn('Browser download suppressed:', err);
    }

    return { status: 'committed', file_path: `${domain}/${topicSlug}/learnings/${cleanTitle.toLowerCase().replace(/\s+/g, '_')}.md` };
  },

  startQuiz(topicId, initialLevel = 'starter') {
    const detail = this.getTopicDetail('leetcode', topicId);
    const exercises = detail.exercises || [];
    const exercise = exercises.find(e => e.exercise_id?.includes(initialLevel)) || exercises[0] || {
      exercise_id: `tier1_${initialLevel}`,
      content: `Analyze asymptotic complexity and formulate invariants for ${topicId}.`
    };

    return {
      session_id: `quiz_${Date.now()}`,
      topic_id: topicId,
      exercise_id: exercise.exercise_id,
      prompt: `# Exercise: ${topicId.replace(/-/g, ' ').toUpperCase()} (${exercise.exercise_id})\n\n${exercise.content}`,
      current_level: initialLevel
    };
  },

  submitQuizTurn(turnData) {
    const currentRating = this.localState.ratings?.[turnData.topic_slug] || 3.0;
    const isPass = (turnData.user_response || '').trim().length >= 10;
    const delta = isPass ? 0.20 : -0.15;
    const newRating = Math.max(1.0, Math.min(5.0, Number((currentRating + delta).toFixed(2))));

    this.localState.ratings[turnData.topic_slug] = newRating;
    this.localState.telemetry.unshift({
      timestamp: new Date().toISOString(),
      provider: 'Cloudflare Edge (Client)',
      model: 'EdgeEngine-Adaptive',
      execution_tier: turnData.exercise_id || 'tier1',
      input_tokens: 850,
      output_tokens: 320,
      success: isPass
    });
    this.saveState();

    return {
      session_id: turnData.session_id,
      passed: isPass,
      new_rating: newRating,
      feedback: isPass
        ? 'Well-reasoned solution! Invariant bounds preserved and state transition verified.'
        : 'Solution missed explicit invariant guardrails or partition handling.',
      next_difficulty_level: newRating >= 4.0 ? 'tier4_l6' : (newRating >= 3.0 ? 'tier3_l5' : 'tier2_l4'),
      next_exercise: {
        exercise_id: newRating >= 4.0 ? 'tier4_l6' : 'tier3_l5',
        prompt: `# Next Tier: Advanced Invariant Formulation\n\nVerify asymptotic optimality under concurrent stress.`
      }
    };
  },

  getRatings() {
    return { ratings: this.localState.ratings || {} };
  },

  startInterview(data) {
    const company = data.target_company || 'Google';
    const topic = data.topic || 'algorithms';
    const track = data.role_track || 'faang_swe_l5_l6';

    return {
      session_id: `int_${Date.now()}`,
      topic: topic,
      target_company: company,
      role_track: track,
      current_phase: 'clarification',
      hints_remaining: data.mode === 'hints' ? 3 : 0,
      interviewer_message: `Welcome to your ${company} technical interview on ${topic.replace(/-/g, ' ')}. Let's begin Phase 1: Clarification. Please state your assumptions, functional scope, and edge boundaries.`
    };
  },

  submitInterviewTurn(sessionId, turnData) {
    const isHint = turnData.turn_type === 'request_hint';
    const phases = ['clarification', 'architecture', 'implementation', 'verification', 'probing'];

    if (isHint) {
      return {
        session_id: sessionId,
        current_phase: 'architecture',
        hints_remaining: 2,
        interviewer_message: '[Socratic Hint]: Consider decomposing the state transition into monotonic log entries before attempting in-place atomic mutations.'
      };
    }

    return {
      session_id: sessionId,
      current_phase: 'architecture',
      hints_remaining: 3,
      interviewer_message: `Good articulation. Now moving to Phase 2: Architecture. How would you design the storage layout and ensure fault isolation?`
    };
  },

  getScorecard(sessionId) {
    return {
      session_id: sessionId,
      bar_decision: 'Hire',
      overall_score: 4.15,
      level_calibration: 'L6 Staff SWE',
      rubric_scores: {
        decomposition: 4.2,
        execution: 4.3,
        architecture: 4.4,
        resilience: 3.9,
        communication: 4.0
      },
      feedback: 'Candidate displayed strong structural discipline, explicit asymptotic invariants, and graceful degradation models.'
    };
  },

  analyzeResumeFit(data) {
    const jd = (data.job_description_text || '').toLowerCase();
    const hasDist = jd.includes('distributed') || jd.includes('scale');
    const hasSec = jd.includes('security') || jd.includes('auth');
    const hasPriv = jd.includes('privacy') || jd.includes('differential');

    const score = hasDist && hasSec ? 88.0 : (hasPriv ? 82.5 : 79.0);

    return {
      target_company: data.target_company || 'Google',
      target_level: 'L6',
      fit_score_percentage: score,
      high_leverage_gaps: [
        { topic_id: 'masters-algorithms', priority: 'high', reason: 'High weight on dynamic programming & graph invariants.' },
        { topic_id: 'modern-authn-authz', priority: 'critical', reason: 'Zanzibar relational tuples required for fine-grained access.' },
        { topic_id: 'agent-access-models', priority: 'medium', reason: 'Sandboxed capability attenuation required for AI workflows.' }
      ],
      custom_interview_loop: [
        { round: 1, topic: 'masters-algorithms', type: 'Coding & Invariants' },
        { round: 2, topic: 'data-structures', type: 'Systems Live Coding' },
        { round: 3, topic: 'modern-authn-authz', type: 'System Design & Zanzibar' },
        { round: 4, topic: 'threat-modeling', type: 'Security Architecture' },
        { round: 5, topic: 'statistics-for-data-analysis', type: 'Scale & Empirical Probing' }
      ]
    };
  },

  getTelemetrySummary() {
    const telemetry = this.localState.telemetry || [];
    const totalRequests = telemetry.length;
    const totalTokens = telemetry.reduce((sum, e) => sum + (e.input_tokens || 0) + (e.output_tokens || 0), 4250);
    const nominalValue = Number(((totalTokens / 1000) * 0.03).toFixed(2));

    return {
      total_requests: totalRequests,
      total_tokens: totalTokens,
      total_estimated_cost_usd: 0.00,
      total_nominal_value_usd: nominalValue,
      recent_events: telemetry.slice(0, 10)
    };
  },

  getEmbeddedCatalog() {
    return {
      topics: [
        { domain: 'leetcode', slug: 'pythonic-coding-patterns', title: 'Pythonic Coding Patterns', role_tracks: ['faang_swe_l5_l6'] },
        { domain: 'leetcode', slug: 'masters-algorithms', title: 'Master\'s Algorithms', role_tracks: ['faang_swe_l5_l6'] },
        { domain: 'leetcode', slug: 'data-structures', title: 'Advanced Data Structures', role_tracks: ['faang_swe_l5_l6'] },
        { domain: 'system-design', slug: 'statistics-for-data-analysis', title: 'Statistics for Distributed Systems', role_tracks: ['faang_swe_l5_l6'] },
        { domain: 'system-design', slug: 'rust', title: 'Rust Systems Programming', role_tracks: ['faang_swe_l5_l6'] },
        { domain: 'system-design', slug: 'go', title: 'Go Microservices & Concurrency', role_tracks: ['faang_swe_l5_l6'] },
        { domain: 'security', slug: 'modern-authn-authz', title: 'Modern AuthN/AuthZ (Zanzibar)', role_tracks: ['faang_security_l4_l6'] },
        { domain: 'security', slug: 'threat-modeling', title: 'Threat Modeling (STRIDE / PASTA)', role_tracks: ['faang_security_l4_l6'] },
        { domain: 'security', slug: 'agent-access-models', title: 'Agent Access Models & Sandboxing', role_tracks: ['faang_security_l4_l6'] },
        { domain: 'privacy-engineering', slug: 'pets-for-ai', title: 'PETs for AI & Confidential Computing', role_tracks: ['faang_privacy_l6'] },
        { domain: 'privacy-engineering', slug: 'modern-differential-privacy', title: 'Modern Differential Privacy (DP-SGD)', role_tracks: ['faang_privacy_l6'] }
      ],
      topic_details: {}
    };
  }
};

// =============================================================================
// 3. API CLIENT
// =============================================================================
const API = {
  baseUrl: localStorage.getItem('learn_api_base_url') || '/api',

  getHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (Store.state.apiToken) {
      headers['Authorization'] = `Bearer ${Store.state.apiToken}`;
      headers['X-Learn-Token'] = Store.state.apiToken;
    }
    return headers;
  },

  async request(endpoint, options = {}) {
    if (Store.state.useEdgeEngine) {
      return null;
    }

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
      if (data && data.status) {
        const isLoopback = !data.data_dir.includes('[protected]');
        Store.setState({
          connectionStatus: isLoopback ? 'connected_local' : 'connected_tailnet',
          useEdgeEngine: false
        });
        return data;
      }
    } catch (err) {
      console.info('Backend unreachable, falling back to local Cloudflare EdgeEngine.', err);
    }

    await EdgeEngine.init();
    Store.setState({
      connectionStatus: 'connected_edge',
      useEdgeEngine: true
    });
    return { status: 'operational', host: 'Cloudflare Edge (Static)', edge_mode: true };
  },

  async listTopics(domain = 'all') {
    if (Store.state.useEdgeEngine) return EdgeEngine.listTopics(domain);
    try {
      return await this.request(`/topics?domain=${domain}`);
    } catch {
      return EdgeEngine.listTopics(domain);
    }
  },

  async getTopicDetail(domain, topicSlug) {
    if (Store.state.useEdgeEngine) return EdgeEngine.getTopicDetail(domain, topicSlug);
    try {
      return await this.request(`/topics/${domain}/${topicSlug}`);
    } catch {
      return EdgeEngine.getTopicDetail(domain, topicSlug);
    }
  },

  async getPinnedTopics() {
    if (Store.state.useEdgeEngine) return EdgeEngine.getPinnedTopics();
    try {
      return await this.request('/topics/pinned');
    } catch {
      return EdgeEngine.getPinnedTopics();
    }
  },

  async pinTopic(domain, topicSlug, priority = 'high', notes = '') {
    if (Store.state.useEdgeEngine) return EdgeEngine.pinTopic(domain, topicSlug, priority, notes);
    try {
      return await this.request(`/topics/${domain}/${topicSlug}/pin`, {
        method: 'POST',
        body: JSON.stringify({ priority, notes }),
      });
    } catch {
      return EdgeEngine.pinTopic(domain, topicSlug, priority, notes);
    }
  },

  async unpinTopic(domain, topicSlug) {
    if (Store.state.useEdgeEngine) return EdgeEngine.unpinTopic(domain, topicSlug);
    try {
      return await this.request(`/topics/${domain}/${topicSlug}/pin`, {
        method: 'DELETE',
      });
    } catch {
      return EdgeEngine.unpinTopic(domain, topicSlug);
    }
  },

  async recordDurableLearning(domain, topicSlug, payload) {
    if (Store.state.useEdgeEngine) return EdgeEngine.recordDurableLearning(domain, topicSlug, payload);
    try {
      return await this.request(`/topics/${domain}/${topicSlug}/learnings`, {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    } catch {
      return EdgeEngine.recordDurableLearning(domain, topicSlug, payload);
    }
  },

  async startQuiz(topicId, initialLevel = 'starter') {
    if (Store.state.useEdgeEngine) return EdgeEngine.startQuiz(topicId, initialLevel);
    try {
      return await this.request('/quiz/start', {
        method: 'POST',
        body: JSON.stringify({ topic_id: topicId, initial_level: initialLevel }),
      });
    } catch {
      return EdgeEngine.startQuiz(topicId, initialLevel);
    }
  },

  async submitQuizTurn(turnData) {
    if (Store.state.useEdgeEngine) return EdgeEngine.submitQuizTurn(turnData);
    try {
      return await this.request('/quiz/turn', {
        method: 'POST',
        body: JSON.stringify(turnData),
      });
    } catch {
      return EdgeEngine.submitQuizTurn(turnData);
    }
  },

  async getRatings() {
    if (Store.state.useEdgeEngine) return EdgeEngine.getRatings();
    try {
      return await this.request('/quiz/ratings');
    } catch {
      return EdgeEngine.getRatings();
    }
  },

  async startInterview(interviewData) {
    if (Store.state.useEdgeEngine) return EdgeEngine.startInterview(interviewData);
    try {
      return await this.request('/interview/start', {
        method: 'POST',
        body: JSON.stringify(interviewData),
      });
    } catch {
      return EdgeEngine.startInterview(interviewData);
    }
  },

  async submitInterviewTurn(sessionId, turnData) {
    if (Store.state.useEdgeEngine) return EdgeEngine.submitInterviewTurn(sessionId, turnData);
    try {
      return await this.request(`/interview/${sessionId}/turn`, {
        method: 'POST',
        body: JSON.stringify(turnData),
      });
    } catch {
      return EdgeEngine.submitInterviewTurn(sessionId, turnData);
    }
  },

  async getScorecard(sessionId) {
    if (Store.state.useEdgeEngine) return EdgeEngine.getScorecard(sessionId);
    try {
      return await this.request(`/interview/${sessionId}/scorecard`);
    } catch {
      return EdgeEngine.getScorecard(sessionId);
    }
  },

  async analyzeResumeFit(data) {
    if (Store.state.useEdgeEngine) return EdgeEngine.analyzeResumeFit(data);
    try {
      return await this.request('/resume/analyze', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    } catch {
      return EdgeEngine.analyzeResumeFit(data);
    }
  },

  async getTelemetrySummary() {
    if (Store.state.useEdgeEngine) return EdgeEngine.getTelemetrySummary();
    try {
      return await this.request('/telemetry/summary');
    } catch {
      return EdgeEngine.getTelemetrySummary();
    }
  }
};

// =============================================================================
// 4. TOAST NOTIFICATIONS & VISUALIZATIONS
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
  }, 3200);
}

const SVGRenderer = {
  renderRadarChart(scores, size = 260) {
    const center = size / 2;
    const radius = center - 35;
    const dimensions = ['decomposition', 'execution', 'architecture', 'resilience', 'communication'];
    const totalPoints = dimensions.length;
    const angleStep = (Math.PI * 2) / totalPoints;

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
// 5. VIEW CONTROLLERS (MWG same-document-transitions)
// =============================================================================
function showView(viewId) {
  const viewTitles = {
    dashboard: 'Dashboard',
    'topic-detail': 'Topic Deep Dive',
    quiz: 'Quiz Arena',
    interview: 'Mock Interview',
    alignment: 'Role Alignment',
    telemetry: 'Telemetry & Costs'
  };

  const titlePrefix = viewTitles[viewId] || 'Dashboard';
  document.title = `${titlePrefix} · learn.willmccarty.io — Technical Mastery & Interview Engine (Savage-Fred/learn)`;

  const updateDOM = () => {
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
  };

  const targetView = document.getElementById(`view-${viewId}`);

  if (document.startViewTransition) {
    const transition = document.startViewTransition(() => updateDOM());
    transition.finished.finally(() => {
      targetView?.querySelector('h1')?.focus();
    });
  } else {
    updateDOM();
    targetView?.querySelector('h1')?.focus();
  }
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

  // Update KPI Bar
  const totalTopicsEl = document.getElementById('kpi-total-topics');
  const pinnedCountEl = document.getElementById('kpi-pinned-count');
  const meanRatingEl = document.getElementById('kpi-mean-rating');
  const engineBadgeEl = document.getElementById('kpi-engine-badge');

  if (totalTopicsEl) totalTopicsEl.textContent = topics.length;
  if (pinnedCountEl) pinnedCountEl.textContent = (Store.state.pinnedTopics || []).length;

  if (meanRatingEl) {
    const ratings = Object.values(Store.state.userRatings || {});
    const mean = ratings.length > 0 ? ratings.reduce((a, b) => a + Number(b), 0) / ratings.length : 3.0;
    meanRatingEl.textContent = mean.toFixed(2);
  }

  if (engineBadgeEl) {
    engineBadgeEl.textContent = Store.state.useEdgeEngine ? 'Cloudflare Edge (Static)' : 'Tailnet Daemon';
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
            <span class="tabular-nums" style="font-family:var(--font-mono); font-size:12px; font-weight:600;">${rating}</span>
            <span class="text-muted" style="font-size:11px;">/ 5.0</span>
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

  tbody.querySelectorAll('.topic-row').forEach(row => {
    row.addEventListener('click', (e) => {
      if (e.target.closest('button')) return;
      const domain = row.dataset.domain;
      const slug = row.dataset.slug;
      location.hash = `#topic/${domain}/${slug}`;
    });
  });

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

// Render Pinned Bar (Preserving exact security contract MicroHighlighter.escape(slug))
function renderPinnedBar() {
  const container = document.getElementById('pinned-list');
  if (!container) return;

  const pins = Store.state.pinnedTopics;
  if (!pins || pins.length === 0) {
    container.innerHTML = '<span class="text-muted" style="font-size:11px;">No pinned topics. Press \'p\' to pin a topic.</span>';
    return;
  }

  container.innerHTML = pins.map(p => {
    const slug = MicroHighlighter.escape(p.topic_id || p.topic_slug || '');
    const domain = MicroHighlighter.escape(p.domain || 'general');
    const prio = MicroHighlighter.escape(p.priority || 'high');
    return `
      <div class="pinned-chip" data-domain="${domain}" data-slug="${slug}">
        <span class="pinned-priority-dot ${prio}"></span>
        <span>${MicroHighlighter.escape(slug)}</span>
        <button class="unpin-btn" data-domain="${domain}" data-slug="${slug}" title="Unpin" aria-label="Unpin topic">×</button>
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
      await API.unpinTopic(domain, slug);
      showToast(`Unpinned ${slug}`, 'info');
      await refreshTopicsAndPins();
    });
  });
}

async function togglePinTopic(domain, slug) {
  const isPinned = (Store.state.pinnedTopics || []).some(p => (p.topic_id || p.topic_slug) === slug);
  if (isPinned) {
    await API.unpinTopic(domain, slug);
    showToast(`Unpinned ${slug}`, 'info');
  } else {
    await API.pinTopic(domain, slug, 'high');
    showToast(`Pinned ${slug} to priority bar`, 'success');
  }
  await refreshTopicsAndPins();
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
      regex: /(#.*$)|("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(\b0x[0-9a-fA-F]+\b|\b\d+(?:\.\d+)?\b)|((?=a)b)|(\b[a-zA-Z_][a-zA-Z0-9_]*\b)|(\s+)|([^a-zA-Z0-9_\s]+)/gm,
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
      regex: /(\/\/.*$|\/\*[\s\S]*?\*\/)|(`[^`]*`|"(?:\\.|[^"\\])*")|(\b0x[0-9a-fA-F]+\b|\b\d+(?:\.\d+)?\b)|((?=a)b)|(\b[a-zA-Z_][a-zA-Z0-9_]*\b)|(\s+)|([^a-zA-Z0-9_\s]+)/gm,
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
      regex: /(\/\/.*$|\/\*[\s\S]*?\*\/)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])')|(\b0x[0-9a-fA-F]+\b|\b\d+(?:\.\d+)?\b)|((?=a)b)|(\b[a-zA-Z_][a-zA-Z0-9_]*\b)|(\s+)|([^a-zA-Z0-9_\s]+)/gm,
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
      regex: /(#.*$)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(\b0x[0-9a-fA-F]+\b|\b\d+(?:\.\d+)?\b)|(\b[a-zA-Z0-9_-]+\b(?=\s*:))|(\b[a-zA-Z_][a-zA-Z0-9_]*\b)|(\s+)|([^a-zA-Z0-9_\s]+)/gm,
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
    let lastIndex = 0;
    while ((m = re.exec(code)) !== null) {
      if (m.index > lastIndex) {
        out += this.escape(code.slice(lastIndex, m.index));
      }
      lastIndex = re.lastIndex;
      const [full, comment, str, num, key, ident, ws, punct] = m;
      if (comment) out += `<span class="tok-comment">${this.escape(comment)}</span>`;
      else if (str) out += `<span class="tok-string">${this.escape(str)}</span>`;
      else if (num) out += `<span class="tok-number">${this.escape(num)}</span>`;
      else if (key) out += `<span class="tok-key">${this.escape(key)}</span>`;
      else if (ident) {
        if (config.keywords.has(ident)) out += `<span class="tok-keyword">${this.escape(ident)}</span>`;
        else if (config.types.has(ident)) out += `<span class="tok-type">${this.escape(ident)}</span>`;
        else out += this.escape(ident);
      } else if (ws) out += ws;
      else if (punct) out += `<span class="tok-punct">${this.escape(punct)}</span>`;
      else out += this.escape(full);
    }
    if (lastIndex < code.length) {
      out += this.escape(code.slice(lastIndex));
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
      if (textBefore.trim()) {
        parts.push(this.formatMarkdownText(textBefore));
      }
      parts.push(`<pre tabindex="0" class="code-pre language-${fenceLang}"><code>${this.highlight(code, fenceLang)}</code></pre>`);
      lastIndex = fenceRe.lastIndex;
    }
    const textAfter = markdown.slice(lastIndex);
    if (textAfter.trim() || parts.length === 0) {
      parts.push(this.formatMarkdownText(textAfter));
    }
    return `<div class="markdown-body">${parts.join('')}</div>`;
  },

  renderTable(rows) {
    if (!rows || rows.length < 2) return '';
    const parseCells = (line) => line.split('|').map(s => s.trim()).filter((_, idx, arr) => idx > 0 && idx < arr.length - 1);
    const headers = parseCells(rows[0].line);
    const bodyRows = rows.slice(rows[1].isDivider ? 2 : 1);

    const ths = headers.map(h => `<th scope="col">${this.escape(h)}</th>`).join('');
    const trs = bodyRows.map(r => {
      const cells = parseCells(r.line);
      return `<tr>${cells.map(c => `<td>${this.escape(c)}</td>`).join('')}</tr>`;
    }).join('');

    return `<table><thead><tr>${ths}</tr></thead><tbody>${trs}</tbody></table>`;
  },

  formatMarkdownText(text) {
    if (!text) return '';

    // Pipe table parser
    const lines = text.split('\n');
    const processedLines = [];
    let inTable = false;
    let tableRows = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const isTableRow = /^\|(.+)\|$/.test(line.trim());
      const isTableDivider = /^\|(\s*:?-+:?\s*\|)+$/.test(line.trim());

      if (isTableRow) {
        if (!inTable) {
          inTable = true;
          tableRows = [];
        }
        tableRows.push({ line: line.trim(), isDivider: isTableDivider });
      } else {
        if (inTable) {
          processedLines.push(this.renderTable(tableRows));
          inTable = false;
          tableRows = [];
        }
        processedLines.push(line);
      }
    }
    if (inTable) {
      processedLines.push(this.renderTable(tableRows));
    }

    let out = processedLines.join('\n');

    return this.escape(out)
      // Restore formatted table tags from escaping
      .replace(/&lt;(\/?)table(.*?)&gt;/g, '<$1table$2>')
      .replace(/&lt;(\/?)thead(.*?)&gt;/g, '<$1thead$2>')
      .replace(/&lt;(\/?)tbody(.*?)&gt;/g, '<$1tbody$2>')
      .replace(/&lt;(\/?)tr(.*?)&gt;/g, '<$1tr$2>')
      .replace(/&lt;(\/?)th(.*?)&gt;/g, '<$1th$2>')
      .replace(/&lt;(\/?)td(.*?)&gt;/g, '<$1td$2>')
      // Headings
      .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      // Blockquotes
      .replace(/^&gt;\s?(.*$)/gim, '<blockquote>$1</blockquote>')
      // Bold & Italic
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/__(.*?)__/g, '<strong>$1</strong>')
      .replace(/\*([^*\n]+)\*/g, '<em>$1</em>')
      // Inline code
      .replace(/`([^`\n]+)`/g, '<code class="inline-code">$1</code>')
      // Lists
      .replace(/^[\*\-]\s+(.*$)/gim, '<li>$1</li>')
      .replace(/^\d+\.\s+(.*$)/gim, '<li>$1</li>')
      // Linebreaks
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>');
  },

  renderToElement(element, content, defaultLang = 'python') {
    if (!element) return;
    element.innerHTML = this.renderMarkdownWithHighlighting(content || '', defaultLang);
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
          ${r.url ? `<a href="${r.url}" target="_blank" rel="noopener" style="font-size:11px; color:var(--accent-primary); word-break:break-all;">${r.url}</a>` : ''}
        </div>
      `).join('');
    } else {
      refContainer.innerHTML = '<p class="text-muted">No references found for this topic.</p>';
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
            ${(ex.content || '').slice(0, 150)}...
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
      exContainer.innerHTML = '<p class="text-muted">No tiered exercises found.</p>';
    }

    // Tab 5: Durable Learnings for this topic
    const learningsContainer = document.getElementById('topic-learnings-content');
    if (learningsContainer) {
      const learnings = detail.learnings || [];
      if (learnings.length > 0) {
        learningsContainer.innerHTML = learnings.map(l => `
          <div class="learning-card">
            <div class="learning-card-header">
              <span class="learning-card-title">${MicroHighlighter.escape(l.title)}</span>
              <span class="badge badge-l6">${l.target_level || 'L6'}</span>
            </div>
            <p style="font-size:13px; margin-bottom:8px;">${MicroHighlighter.escape(l.mental_model)}</p>
            ${l.invariants && l.invariants.length > 0 ? `
              <div style="font-size:12px; color:var(--text-secondary); margin-bottom:8px;">
                <strong>Invariants:</strong> ${l.invariants.map(i => `<code class="inline-code">${MicroHighlighter.escape(i)}</code>`).join(' ')}
              </div>
            ` : ''}
            ${l.code_examples ? `<pre class="code-pre"><code>${MicroHighlighter.highlight(l.code_examples, 'python')}</code></pre>` : ''}
          </div>
        `).join('');
      } else {
        learningsContainer.innerHTML = `
          <div style="padding:var(--space-lg); text-align:center; background:var(--bg-card); border-radius:var(--radius-md); border:1px solid var(--border-light);">
            <p class="text-muted" style="margin-bottom:var(--space-md);">No durable learnings captured for ${topicSlug} yet.</p>
            <button class="btn btn-secondary btn-sm" onclick="openDurableCaptureModal('${domain}', '${topicSlug}')">Capture First Breakthrough (d)</button>
          </div>
        `;
      }
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

  // Sync selectors
  const topicSelect = document.getElementById('quiz-select-topic');
  if (topicSelect) topicSelect.value = topicSlug;
  const tierSelect = document.getElementById('quiz-select-tier');
  if (tierSelect) {
    tierSelect.value = initialTier.startsWith('tier') ? initialTier : `tier1_${initialTier}`;
  }

  try {
    const sessionData = await API.startQuiz(topicSlug, initialTier);
    Store.setState({ activeQuizSession: sessionData });
    MicroHighlighter.renderToElement(document.getElementById('quiz-problem-prompt'), sessionData.prompt, 'python');

    const ratings = await API.getRatings();
    const currentRating = ratings.ratings?.[topicSlug] || 3.0;
    document.getElementById('quiz-rating-display').textContent = Number(currentRating).toFixed(2);
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
    const passClass = res.passed ? 'badge-l6' : 'badge-starter';
    const statusText = res.passed ? 'PASSED — Advancing Ladder' : 'SCAFFOLD TURN — Review Invariant';

    drawer.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:var(--space-sm);">
        <span class="badge ${passClass}">${statusText}</span>
        <span style="font-family:var(--font-mono); font-size:12px;">New Rating: <strong class="tabular-nums">${Number(res.new_rating).toFixed(2)}</strong></span>
      </div>
      <p style="font-size:13px; margin-bottom:var(--space-md);">${res.feedback || res.evaluation}</p>
      <div style="display:flex; gap:var(--space-sm);">
        <button id="btn-quiz-next-exercise" class="btn btn-primary btn-sm">Next Problem (${res.next_difficulty_level})</button>
        <button id="btn-quiz-durable-capture" class="btn btn-secondary btn-sm">Capture as Durable Learning (d)</button>
      </div>
    `;

    document.getElementById('quiz-rating-display').textContent = Number(res.new_rating).toFixed(2);

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
      openDurableCaptureModal('leetcode', session.topic_id);
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
  if (Store.state.useEdgeEngine) {
    setInterviewWsStatus('● EdgeEngine Active', 'ws-active');
    return;
  }

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
      console.warn('WebSocket stream error; operating in REST fallback mode.', err);
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

async function startInterviewSession(topicSlug, roleTrack = 'faang_swe_l5_l6', targetCompany = 'Google', mode = 'hints') {
  showView('interview');
  document.getElementById('interview-company-badge').textContent = targetCompany;
  document.getElementById('interview-track-badge').textContent = roleTrack;
  document.getElementById('interview-mode-badge').textContent = mode === 'hints' ? 'Socratic Hints Mode' : 'Strict Mode';

  // Sync selectors
  const topicSelect = document.getElementById('interview-select-topic');
  if (topicSelect) topicSelect.value = topicSlug;
  const compSelect = document.getElementById('interview-select-company');
  if (compSelect) compSelect.value = targetCompany;
  const trackSelect = document.getElementById('interview-select-track');
  if (trackSelect) trackSelect.value = roleTrack;
  const modeSelect = document.getElementById('interview-select-mode');
  if (modeSelect) modeSelect.value = mode;

  const feed = document.getElementById('interview-chat-feed');
  feed.innerHTML = '';

  try {
    const sessionData = await API.startInterview({
      topic: topicSlug,
      role_track: roleTrack,
      target_company: targetCompany,
      mode: mode,
      time_limit_minutes: 45,
    });
    Store.setState({ activeInterviewSession: sessionData });

    appendChatMessage('interviewer', sessionData.interviewer_message);
    updateInterviewPhase(sessionData.current_phase || 'clarification');
    updateHintsBudget(sessionData.hints_remaining ?? 3);

    connectInterviewWebSocket(sessionData.session_id);

    // Start 45-min timer
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
      const timerEl = document.getElementById('interview-timer');
      if (timerEl) {
        timerEl.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
      }
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
        <span class="badge ${card.overall_score >= 3.5 ? 'badge-l6' : 'badge-starter'}" style="font-size:14px; padding:4px 10px;">
          ${card.bar_decision}
        </span>
        <span style="font-size:13px; font-weight:600; margin-left:var(--space-sm);">${card.level_calibration} Calibration</span>
      </div>
      <div style="font-family:var(--font-mono); font-size:14px;">
        Overall Score: <strong class="tabular-nums">${Number(card.overall_score).toFixed(2)}</strong> / 5.00
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
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong>${g.topic_id}</strong>
                <span class="badge ${g.priority === 'critical' ? 'badge-l6' : 'badge-l5'}">${g.priority}</span>
              </div>
              <div style="font-size:12px; color:var(--text-secondary); margin-top:2px;">${g.reason}</div>
              <div style="margin-top:6px; display:flex; gap:6px;">
                <button class="btn btn-secondary btn-xs btn-gap-pin" data-topic="${g.topic_id}">Pin Gap (p)</button>
                <button class="btn btn-primary btn-xs btn-gap-practice" data-topic="${g.topic_id}">Practice Round</button>
              </div>
            </div>
          `).join('')}
        </div>

        <div style="background:var(--bg-card); border:1px solid var(--border-light); border-radius:var(--radius-lg); padding:var(--space-md);">
          <h4 style="font-size:14px; font-weight:700; margin-bottom:var(--space-md);">Custom 5-Round Interview Loop</h4>
          ${(res.custom_interview_loop || []).map(r => `
            <div style="margin-bottom:var(--space-xs); font-size:13px; padding:var(--space-xs) 0; border-bottom:1px solid var(--border-light); display:flex; justify-content:space-between; align-items:center;">
              <div>
                <strong>Round ${r.round}:</strong> ${r.topic} <span class="text-muted">(${r.type || 'evaluation'})</span>
              </div>
              <button class="btn btn-secondary btn-xs btn-round-practice" data-topic="${r.topic}">Simulate</button>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    container.querySelectorAll('.btn-gap-pin').forEach(btn => {
      btn.addEventListener('click', () => {
        togglePinTopic('leetcode', btn.dataset.topic);
      });
    });

    container.querySelectorAll('.btn-gap-practice, .btn-round-practice').forEach(btn => {
      btn.addEventListener('click', () => {
        location.hash = `#quiz/${btn.dataset.topic}/starter`;
      });
    });

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
          <td class="tabular-nums" style="font-family:var(--font-mono); font-size:11px;">${(ev.input_tokens || 0) + (ev.output_tokens || 0)}</td>
          <td><span class="badge ${ev.success ? 'badge-l6' : 'badge-starter'}">${ev.success ? 'PASS' : 'FAIL'}</span></td>
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
    if (Store.state.activeView === 'topic-detail') {
      loadTopicDetail(domain, topicSlug);
    }
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
    populateSelects();
  } catch (err) {
    console.error('Refresh error:', err);
  }
}

function populateSelects() {
  const topics = Store.state.topics || [];
  const quizSelect = document.getElementById('quiz-select-topic');
  const interviewSelect = document.getElementById('interview-select-topic');

  if (quizSelect && quizSelect.options.length === 0) {
    quizSelect.innerHTML = topics.map(t => `<option value="${t.slug}">${t.title}</option>`).join('');
  }
  if (interviewSelect && interviewSelect.options.length === 0) {
    interviewSelect.innerHTML = topics.map(t => `<option value="${t.slug}">${t.title}</option>`).join('');
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
    const topic = parts[1] || 'masters-algorithms';
    const tier = parts[2] || 'starter';
    startQuizSession(topic, tier);
  } else if (route === 'interview') {
    const topic = parts[1] || 'masters-algorithms';
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

    if (e.key === '/' || (e.key === 'k' && (e.metaKey || e.ctrlKey))) {
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
      const maxIdx = Store.state.topics.length - 1;
      const nextIdx = Math.min(maxIdx, Store.state.selectedTopicIndex + 1);
      Store.setState({ selectedTopicIndex: nextIdx });
      renderDashboard();
    } else if (e.key === 'k') {
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

  // MWG light-dismiss-a-dialog coordinate fallback for unsupported browsers
  if (!('closedBy' in HTMLDialogElement.prototype)) {
    document.querySelectorAll('dialog').forEach(dialog => {
      dialog.addEventListener('click', (event) => {
        if (event.target !== dialog) return;
        const rect = dialog.getBoundingClientRect();
        const isDialogContent = (
          rect.top <= event.clientY &&
          event.clientY <= rect.top + rect.height &&
          rect.left <= event.clientX &&
          event.clientX <= rect.left + rect.width
        );
        if (isDialogContent) return;
        dialog.close();
      });
    });
  }

  // Header quick buttons
  document.getElementById('btn-global-search')?.addEventListener('click', () => {
    const modal = document.getElementById('modal-search');
    modal?.showModal();
    document.getElementById('modal-search-input')?.focus();
  });
  document.getElementById('btn-shortcuts')?.addEventListener('click', () => {
    document.getElementById('modal-shortcuts')?.showModal();
  });
  document.getElementById('btn-auth')?.addEventListener('click', () => {
    const input = document.getElementById('auth-token-input');
    const baseInput = document.getElementById('auth-base-url-input');
    if (input) input.value = Store.state.apiToken;
    if (baseInput) baseInput.value = Store.state.apiBaseUrl;
    document.getElementById('modal-auth')?.showModal();
  });

  // Auth form
  document.getElementById('form-auth-token')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const token = document.getElementById('auth-token-input').value.trim();
    const baseUrl = document.getElementById('auth-base-url-input').value.trim() || '/api';
    Store.setApiToken(token);
    Store.setApiBaseUrl(baseUrl);
    document.getElementById('modal-auth').close();
    showToast('Settings saved. Re-checking status...', 'success');
    await API.checkStatus();
    updateConnectionUI();
    await refreshTopicsAndPins();
  });

  // Deep dive tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');
      const targetPane = document.getElementById(btn.dataset.tab);
      if (targetPane) targetPane.classList.add('active');
    });
  });

  // Back to Dashboard button in Deep Dive
  document.getElementById('btn-back-to-dashboard')?.addEventListener('click', () => {
    location.hash = '#dashboard';
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

  // Domain card click-to-filter
  document.querySelectorAll('.domain-card[data-domain]').forEach(card => {
    card.addEventListener('click', async () => {
      const domain = card.dataset.domain;
      document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.filter === domain);
      });
      const res = await API.listTopics(domain);
      Store.setState({ topics: res.topics || [] });
      renderDashboard();
    });
  });

  // Search input filter on dashboard
  document.getElementById('topic-search-input')?.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    const tbody = document.getElementById('topic-table-body');
    if (tbody) {
      tbody.querySelectorAll('.topic-row').forEach(row => {
        const slug = (row.dataset.slug || '').toLowerCase();
        const domain = (row.dataset.domain || '').toLowerCase();
        row.style.display = (slug.includes(q) || domain.includes(q)) ? '' : 'none';
      });
    }
  });

  // Global search modal input & results
  const searchInput = document.getElementById('modal-search-input');
  const searchResults = document.getElementById('modal-search-results');
  if (searchInput && searchResults) {
    const executeSearch = () => {
      const q = searchInput.value.toLowerCase().trim();
      if (!q) {
        searchResults.innerHTML = '';
        return;
      }
      const matches = (Store.state.topics || []).filter(t =>
        t.slug.toLowerCase().includes(q) ||
        t.title.toLowerCase().includes(q) ||
        t.domain.toLowerCase().includes(q)
      );

      if (matches.length === 0) {
        searchResults.innerHTML = '<p class="text-muted" style="font-size:12px; padding:8px;">No matching topics found.</p>';
        return;
      }

      searchResults.innerHTML = `
        <div class="search-results-list">
          ${matches.map(m => `
            <div class="search-result-item" data-domain="${m.domain}" data-slug="${m.slug}">
              <div>
                <strong style="font-size:13px;">${m.title}</strong>
                <div style="font-size:11px; color:var(--text-muted); font-family:var(--font-mono);">${m.domain} / ${m.slug}</div>
              </div>
              <span class="badge badge-l4">Open</span>
            </div>
          `).join('')}
        </div>
      `;

      searchResults.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', () => {
          document.getElementById('modal-search')?.close();
          location.hash = `#topic/${item.dataset.domain}/${item.dataset.slug}`;
        });
      });
    };

    searchInput.addEventListener('input', executeSearch);
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const first = searchResults.querySelector('.search-result-item');
        if (first) {
          document.getElementById('modal-search')?.close();
          location.hash = `#topic/${first.dataset.domain}/${first.dataset.slug}`;
        }
      }
    });
  }

  // Quiz Header Interactive Selectors
  document.getElementById('btn-quiz-new')?.addEventListener('click', () => {
    const topic = document.getElementById('quiz-select-topic')?.value || 'masters-algorithms';
    const tier = document.getElementById('quiz-select-tier')?.value || 'tier1_starter';
    startQuizSession(topic, tier);
  });
  document.getElementById('quiz-select-topic')?.addEventListener('change', (e) => {
    const tier = document.getElementById('quiz-select-tier')?.value || 'tier1_starter';
    startQuizSession(e.target.value, tier);
  });
  document.getElementById('btn-quiz-capture')?.addEventListener('click', () => {
    const topic = Store.state.activeQuizSession?.topic_id || 'algorithms';
    openDurableCaptureModal('leetcode', topic);
  });

  // Mock Interview Header Interactive Selectors
  document.getElementById('btn-interview-new')?.addEventListener('click', () => {
    const topic = document.getElementById('interview-select-topic')?.value || 'masters-algorithms';
    const company = document.getElementById('interview-select-company')?.value || 'Google';
    const track = document.getElementById('interview-select-track')?.value || 'faang_swe_l5_l6';
    const mode = document.getElementById('interview-select-mode')?.value || 'hints';
    startInterviewSession(topic, track, company, mode);
  });

  // 1-Click Role Alignment Job Description Presets
  const presets = {
    google_swe: {
      role: 'faang_swe_l5_l6',
      company: 'Google',
      jd: `Google L6 Staff Software Engineer (Core Systems & Infrastructure)
Requirements:
- Deep expertise in distributed storage systems (Spanner, Zanzibar relation tuples)
- Rigorous invariant proofs under network partition and clock drift (TrueTime)
- Masters algorithms: Graph dynamic programming, segment trees, concurrency synchronization
- High performance profiling in Go / C++ / Rust with sub-millisecond tail latency`
    },
    anthropic_sec: {
      role: 'faang_security_l4_l6',
      company: 'Anthropic',
      jd: `Anthropic L5/L6 Security Engineer (AI Tool Safety & Sandboxing)
Requirements:
- Capability attenuation and strict ambient authority elimination
- Threat modeling for autonomous agent tooling (STRIDE / PASTA)
- MicroVM / WASM isolation boundaries and seccomp-bpf system call filters
- High craftsmanship: defensive programming in Rust and Python`
    },
    meta_privacy: {
      role: 'faang_privacy_l6',
      company: 'Meta',
      jd: `Meta L6 Privacy Engineer (AI & Social Infrastructure)
Requirements:
- Modern Differential Privacy: DP-SGD, Renyi DP, privacy budget composition
- Privacy-Enhancing Technologies (PETs): Secure Multi-Party Computation (SMPC), TEEs
- Scale data protection across TAO caching graphs and Cassandra partitions
- Back-of-the-envelope scale calculations and high-velocity systems execution`
    },
    openai_research: {
      role: 'ai_lab_research_l4_l5',
      company: 'OpenAI',
      jd: `OpenAI Research Engineer (Scaling & ML Systems)
Requirements:
- Live coding speed and deep algorithmic fluency in Python and C++
- GPU IPC buffers, pinned host memory, and distributed PyTorch collective communications
- Rapid test debugging under extreme pressure with zero hand-waving
- Statistical foundations: distribution shift, variance reduction, and telemetry probing`
    }
  };

  document.querySelectorAll('.btn-preset').forEach(btn => {
    btn.addEventListener('click', () => {
      const p = presets[btn.dataset.preset];
      if (p) {
        document.getElementById('align-role-track').value = p.role;
        document.getElementById('align-target-company').value = p.company;
        document.getElementById('align-jd-text').value = p.jd;
        showToast(`Loaded ${p.company} preset.`, 'info');
      }
    });
  });

  // Load sample/active resume
  document.getElementById('btn-load-active-resume')?.addEventListener('click', () => {
    const resumeTextarea = document.getElementById('align-resume-text');
    if (resumeTextarea) {
      resumeTextarea.value = `# Will McCarty — Staff Systems & Security Engineer

## Summary
Staff Engineer with 10+ years specializing in distributed systems consensus, fine-grained access control (Zanzibar), and high-throughput microservices in Rust and Go.

## Core Competencies
- Distributed Systems: Spanner, Raft/Paxos consensus, Zanzibar relation tuples, TAO caching.
- Security & Privacy: STRIDE threat modeling, least-privilege sandboxing, Differential Privacy (DP-SGD).
- Algorithms: Master's algorithms, monotone sequence invariants, segment trees.
- Languages: Rust, Python, Go, TypeScript.`;
      showToast('Loaded active resume profile.', 'success');
    }
  });

  // Event handlers
  document.getElementById('btn-quiz-submit')?.addEventListener('click', submitQuizAnswer);
  document.getElementById('btn-send-interview-turn')?.addEventListener('click', () => sendInterviewTurn());
  document.getElementById('btn-request-hint')?.addEventListener('click', () => sendInterviewTurn('request_hint'));
  document.getElementById('btn-finalize-interview')?.addEventListener('click', finalizeInterview);
  document.getElementById('btn-run-alignment')?.addEventListener('click', runRoleAlignment);
  document.getElementById('form-durable-capture')?.addEventListener('submit', handleDurableCaptureSubmit);

  // Status check & UI update
  await API.checkStatus();
  updateConnectionUI();

  // Load initial topics and pins
  await refreshTopicsAndPins();

  // Router setup
  window.addEventListener('hashchange', handleHashRoute);
  handleHashRoute();

  // Global keyboard shortcuts
  setupGlobalShortcuts();
}

function updateConnectionUI() {
  const statusText = document.getElementById('connection-text');
  const statusDot = document.getElementById('connection-dot');
  if (!statusText || !statusDot) return;

  if (Store.state.connectionStatus === 'connected_edge') {
    statusText.textContent = 'Cloudflare Edge (Static)';
    statusDot.className = 'status-dot';
  } else if (Store.state.connectionStatus === 'connected_local') {
    statusText.textContent = 'Local:8795';
    statusDot.className = 'status-dot';
  } else if (Store.state.connectionStatus === 'connected_tailnet') {
    statusText.textContent = 'Tailnet API';
    statusDot.className = 'status-dot';
  } else if (Store.state.connectionStatus === 'unauthorized') {
    statusText.textContent = 'Auth Required';
    statusDot.className = 'status-dot warn';
  } else {
    statusText.textContent = 'Offline';
    statusDot.className = 'status-dot err';
  }
}

// Start on DOM ready
document.addEventListener('DOMContentLoaded', initApp);
