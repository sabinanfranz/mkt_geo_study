// GEO Mentoring Learning — Frontend Logic

const API = "";
const app = document.getElementById("app");
const badge = document.getElementById("health-badge");

// ──────────────────────────────────────────
// Dark Mode
// ──────────────────────────────────────────
function initTheme() {
  const saved = localStorage.getItem('theme');
  if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    document.documentElement.setAttribute('data-theme', 'dark');
    updateThemeIcon(true);
  }
}

function toggleTheme() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  if (isDark) {
    document.documentElement.removeAttribute('data-theme');
    localStorage.setItem('theme', 'light');
    updateThemeIcon(false);
  } else {
    document.documentElement.setAttribute('data-theme', 'dark');
    localStorage.setItem('theme', 'dark');
    updateThemeIcon(true);
  }
}

function updateThemeIcon(isDark) {
  const btn = document.getElementById('theme-toggle');
  if (btn) {
    btn.innerHTML = isDark ? '&#9788;' : '&#9790;';
    btn.title = isDark ? '라이트 모드' : '다크 모드';
  }
}

initTheme();

// ──────────────────────────────────────────
// Markdown Config (XSS prevention)
// ──────────────────────────────────────────
if (typeof marked !== "undefined") {
  marked.setOptions({ breaks: true });
}

// ──────────────────────────────────────────
// Health Check
// ──────────────────────────────────────────
async function checkHealth() {
  try {
    const res = await fetch(`${API}/api/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    badge.textContent = "online";
    badge.className = "badge badge--ok";
  } catch {
    badge.textContent = "offline";
    badge.className = "badge badge--error";
  }
}

// ──────────────────────────────────────────
// API Functions
// ──────────────────────────────────────────
async function apiCall(endpoint, options = {}) {
  try {
    const res = await fetch(`${API}${endpoint}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("API Error:", err);
    throw err;
  }
}

async function fetchStages() {
  return apiCall("/api/stages");
}

async function fetchModules(stageId) {
  return apiCall(`/api/stages/${stageId}/modules`);
}

async function fetchSteps(moduleId) {
  return apiCall(`/api/modules/${moduleId}/steps`);
}

async function submitAnswer(stepId, optionId) {
  const timeSpent = getStepElapsedSeconds(stepId);
  const body = optionId != null
    ? { selected_option_id: optionId, time_spent_seconds: timeSpent }
    : { selected_option_id: null, time_spent_seconds: timeSpent };
  return apiCall(`/api/steps/${stepId}/answer`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

async function fetchProgress() {
  return apiCall("/api/progress");
}

async function fetchAdminStats() {
  return apiCall("/api/admin/stats");
}

async function evaluateStage(stageId) {
  return apiCall(`/api/stages/${stageId}/evaluate`, {
    method: "POST",
  });
}

async function toggleBookmark(stepId) {
  return apiCall(`/api/bookmarks/${stepId}`, { method: "POST" });
}

async function fetchBookmarks() {
  return apiCall("/api/bookmarks");
}

// ──────────────────────────────────────────
// State Helpers
// ──────────────────────────────────────────
function showLoading(container) {
  container.innerHTML = `
    <div class="loading">
      <div class="spinner"></div>
      <p>로딩 중...</p>
    </div>`;
}

function showError(container, message, retryFn) {
  container.innerHTML = `
    <div class="error">
      <p>${escapeHtml(message)}</p>
      <button class="btn btn-primary" id="retry-btn">다시 시도</button>
    </div>`;
  if (retryFn) {
    document.getElementById("retry-btn").addEventListener("click", retryFn);
  }
}

function showEmpty(container, message) {
  container.innerHTML = `
    <div class="empty">
      <p>${escapeHtml(message || "아직 데이터가 없습니다.")}</p>
    </div>`;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ──────────────────────────────────────────
// Router
// ──────────────────────────────────────────
function getRoute() {
  const hash = location.hash || "#/";
  return hash;
}

function navigate(hash) {
  location.hash = hash;
}

function router() {
  const hash = getRoute();

  // #/admin/content
  if (hash === "#/admin/content") {
    renderAdminContent();
    return;
  }

  // #/admin/module/{id}/result (admin context)
  const adminResultMatch = hash.match(/^#\/admin\/module\/(\d+)\/result$/);
  if (adminResultMatch) {
    renderResult(parseInt(adminResultMatch[1]), true);
    return;
  }

  // #/admin/module/{id} (admin context)
  const adminModuleMatch = hash.match(/^#\/admin\/module\/(\d+)$/);
  if (adminModuleMatch) {
    renderLearning(parseInt(adminModuleMatch[1]), true);
    return;
  }

  // #/admin
  if (hash === "#/admin") {
    renderAdminStats();
    return;
  }

  // #/module/{id}/result
  const resultMatch = hash.match(/^#\/module\/(\d+)\/result$/);
  if (resultMatch) {
    renderResult(parseInt(resultMatch[1]));
    return;
  }

  // #/module/{id}
  const moduleMatch = hash.match(/^#\/module\/(\d+)$/);
  if (moduleMatch) {
    renderLearning(parseInt(moduleMatch[1]));
    return;
  }

  // #/stage/{id}
  const stageMatch = hash.match(/^#\/stage\/(\d+)$/);
  if (stageMatch) {
    renderModuleList(parseInt(stageMatch[1]));
    return;
  }

  // Default: dashboard
  renderDashboard();
}

window.addEventListener("hashchange", router);

// ──────────────────────────────────────────
// Admin Content Viewer
// ──────────────────────────────────────────
async function renderAdminContent() {
  showLoading(app);

  try {
    const stages = await fetchStages();

    if (!stages || stages.length === 0) {
      showEmpty(app, "콘텐츠가 아직 준비되지 않았습니다.");
      return;
    }

    // Fetch modules for all stages in parallel
    const modulesPerStage = await Promise.all(
      stages.map(stage => fetchModules(stage.id))
    );

    // Fetch steps for all modules in parallel
    const allModuleIds = [];
    const moduleStageMap = {};
    modulesPerStage.forEach((modules, idx) => {
      modules.forEach(mod => {
        allModuleIds.push(mod.id);
        moduleStageMap[mod.id] = stages[idx];
      });
    });

    const stepsPerModule = await Promise.all(
      allModuleIds.map(modId => fetchSteps(modId).catch(() => []))
    );

    // Build a map: moduleId -> steps
    const stepsMap = {};
    allModuleIds.forEach((modId, idx) => {
      stepsMap[modId] = stepsPerModule[idx] || [];
    });

    // Calculate totals
    let totalModules = 0;
    let totalSteps = 0;
    modulesPerStage.forEach(modules => {
      totalModules += modules.length;
      modules.forEach(mod => {
        totalSteps += (stepsMap[mod.id] || []).length;
      });
    });

    // Build HTML
    let html = `
      <a class="back-link" onclick="navigate('#/')">&larr; 대시보드로</a>
      <div class="admin-content-header">
        <h2 class="section-title">관리자 콘텐츠 열람</h2>
        <p class="section-desc">모든 Stage와 Module을 잠금 없이 열람할 수 있습니다.</p>
      </div>

      <div class="admin-content-stats">
        <span class="admin-content-stat-item">${stages.length} Stages</span>
        <span class="admin-content-stat-sep">|</span>
        <span class="admin-content-stat-item">${totalModules} Modules</span>
        <span class="admin-content-stat-sep">|</span>
        <span class="admin-content-stat-item">${totalSteps} Steps</span>
      </div>
    `;

    stages.forEach((stage, stageIdx) => {
      const modules = modulesPerStage[stageIdx] || [];
      const isLocked = !stage.is_unlocked;

      html += `
        <div class="admin-stage-section">
          <div class="admin-stage-header" onclick="this.parentElement.classList.toggle('collapsed')">
            <div class="admin-stage-header-left">
              <span class="admin-stage-arrow">&#9660;</span>
              <span class="admin-stage-title">Stage ${stage.order_idx}: ${escapeHtml(stage.title)}</span>
              ${isLocked ? '<span class="admin-lock-badge">&#128274; 잠김</span>' : ''}
            </div>
            <span class="admin-stage-count">${modules.length} modules</span>
          </div>
          <div class="admin-stage-body">
      `;

      modules.forEach(mod => {
        const steps = stepsMap[mod.id] || [];
        const stepCount = steps.length;

        // Count step types
        const typeCounts = { reading: 0, quiz: 0, practice: 0 };
        steps.forEach(s => {
          if (typeCounts.hasOwnProperty(s.type)) {
            typeCounts[s.type]++;
          }
        });

        const typeParts = [];
        if (typeCounts.reading > 0) typeParts.push(`reading ${typeCounts.reading}`);
        if (typeCounts.quiz > 0) typeParts.push(`quiz ${typeCounts.quiz}`);
        if (typeCounts.practice > 0) typeParts.push(`practice ${typeCounts.practice}`);
        const typeStr = typeParts.length > 0 ? ` (${typeParts.join(', ')})` : '';

        // Completion status
        const isCompleted = mod.completed_steps >= mod.total_steps && mod.total_steps > 0;
        const isInProgress = mod.completed_steps > 0 && !isCompleted;
        let statusHtml = '';
        if (isCompleted) {
          statusHtml = '<span class="admin-module-status completed">&#10003; 완료</span>';
        } else if (isInProgress) {
          statusHtml = `<span class="admin-module-status in-progress">${mod.completed_steps}/${mod.total_steps}</span>`;
        } else {
          statusHtml = '<span class="admin-module-status not-started">미완료</span>';
        }

        html += `
          <div class="admin-module-row" onclick="navigate('#/admin/module/${mod.id}')">
            <div class="admin-module-info">
              <span class="admin-module-number">[모듈 ${stage.order_idx}-${mod.order_idx}]</span>
              <span class="admin-module-title">${escapeHtml(mod.title)}</span>
            </div>
            <div class="admin-module-meta">
              <span class="admin-step-badge">${stepCount} steps${typeStr}</span>
              ${statusHtml}
              <span class="admin-module-go">&rarr; 열람</span>
            </div>
          </div>
        `;
      });

      html += `
          </div>
        </div>
      `;
    });

    html += `
      <div class="admin-link-section">
        <button class="btn btn-secondary" onclick="navigate('#/admin')">학습 통계 보기</button>
      </div>
    `;

    app.innerHTML = html;
  } catch (err) {
    showError(app, "콘텐츠를 불러올 수 없습니다.", renderAdminContent);
  }
}

// ──────────────────────────────────────────
// Admin Stats Dashboard (US-024)
// ──────────────────────────────────────────
async function renderAdminStats() {
  showLoading(app);

  try {
    const stats = await fetchAdminStats();

    // Format time
    const hours = Math.floor(stats.total_time_seconds / 3600);
    const mins = Math.floor((stats.total_time_seconds % 3600) / 60);
    const timeStr = hours > 0 ? `${hours}시간 ${mins}분` : `${mins}분`;

    const completionPct = stats.total_steps > 0
      ? Math.round((stats.total_steps_completed / stats.total_steps) * 100)
      : 0;

    let html = `
      <a class="back-link" onclick="navigate('#/')">&larr; 대시보드로</a>
      <h2 class="section-title">학습 통계</h2>

      <div class="admin-summary">
        <div class="stat-card">
          <div class="stat-value">${completionPct}%</div>
          <div class="stat-label">전체 진도</div>
          <div class="stat-sub">${stats.total_steps_completed} / ${stats.total_steps} Steps</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${stats.overall_accuracy_pct != null ? stats.overall_accuracy_pct + '%' : '-'}</div>
          <div class="stat-label">전체 정답률</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${timeStr}</div>
          <div class="stat-label">총 학습 시간</div>
        </div>
      </div>
    `;

    // Weakest modules
    if (stats.weakest_modules && stats.weakest_modules.length > 0) {
      html += `<div class="admin-section">
        <h3>취약 모듈 (정답률 하위)</h3>
        <div class="weak-list">`;
      stats.weakest_modules.forEach(m => {
        const accStr = m.accuracy_pct != null ? m.accuracy_pct + '%' : '-';
        html += `
          <div class="weak-item">
            <span class="weak-title">${escapeHtml(m.module_title)}</span>
            <span class="weak-accuracy">${accStr}</span>
          </div>`;
      });
      html += `</div></div>`;
    }

    // Module detail table
    html += `<div class="admin-section">
      <h3>모듈별 상세</h3>
      <div class="admin-table-wrap">
        <table class="admin-table">
          <thead>
            <tr>
              <th>모듈</th>
              <th>Stage</th>
              <th>진도</th>
              <th>정답률</th>
              <th>정답</th>
              <th>오답</th>
              <th>평균시간</th>
            </tr>
          </thead>
          <tbody>`;

    stats.modules.forEach(m => {
      const progStr = `${m.completed_steps}/${m.total_steps}`;
      const accStr = m.accuracy_pct != null ? m.accuracy_pct + '%' : '-';
      const timeStr2 = m.avg_time_seconds != null ? Math.round(m.avg_time_seconds) + '초' : '-';
      const rowClass = m.accuracy_pct != null && m.accuracy_pct < 70 ? 'weak-row' : '';
      html += `
        <tr class="${rowClass}">
          <td>${escapeHtml(m.module_title)}</td>
          <td>Stage ${m.stage_id}</td>
          <td>${progStr}</td>
          <td>${accStr}</td>
          <td>${m.correct_answers}</td>
          <td>${m.wrong_answers}</td>
          <td>${timeStr2}</td>
        </tr>`;
    });

    html += `</tbody></table></div></div>`;

    html += `<div class="admin-link-section">
      <button class="btn btn-secondary" onclick="navigate('#/admin/content')">전체 콘텐츠 열람</button>
    </div>`;

    app.innerHTML = html;
  } catch (err) {
    showError(app, "통계를 불러올 수 없습니다.", renderAdminStats);
  }
}

// ──────────────────────────────────────────
// Dashboard
// ──────────────────────────────────────────
async function renderDashboard() {
  showLoading(app);

  try {
    const stages = await fetchStages();

    if (!stages || stages.length === 0) {
      showEmpty(app, "아직 학습 콘텐츠가 준비되지 않았습니다.");
      return;
    }

    const totalCompleted = stages.reduce((s, st) => s + st.completed_modules, 0);
    const totalModules = stages.reduce((s, st) => s + st.total_modules, 0);
    const overallPct = totalModules > 0 ? Math.round((totalCompleted / totalModules) * 100) : 0;

    let html = `
      <div class="overall-progress">
        <h2>전체 진도</h2>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${overallPct}%"></div>
        </div>
        <div class="progress-label">${totalCompleted} / ${totalModules} 모듈 완료 (${overallPct}%)</div>
      </div>
    `;

    stages.forEach((stage) => {
      const pct = stage.total_modules > 0
        ? Math.round((stage.completed_modules / stage.total_modules) * 100)
        : 0;
      const isLocked = !stage.is_unlocked;
      const cardClass = isLocked ? "stage-card locked" : "stage-card";

      html += `
        <div class="${cardClass}" data-stage-id="${stage.id}" ${isLocked ? "" : `onclick="navigate('#/stage/${stage.id}')"` }>
          <h3>
            Stage ${stage.order_idx}: ${escapeHtml(stage.title)}
            ${isLocked ? '<span class="lock-icon">&#128274;</span>' : ""}
          </h3>
          <p class="stage-desc">${escapeHtml(stage.description)}</p>
          <p class="stage-progress-label">모듈 진도: ${stage.completed_modules} / ${stage.total_modules}</p>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${pct}%"></div>
          </div>
          ${isLocked ? '<p class="lock-message">이전 Stage 완료 후 해제됩니다.</p>' : ""}
        </div>
      `;
    });

    html += `<div class="admin-link-section">
      <button class="btn btn-secondary" onclick="navigate('#/admin')">학습 통계 보기</button>
      <button class="btn btn-secondary" onclick="navigate('#/admin/content')">전체 콘텐츠 열람</button>
    </div>`;

    app.innerHTML = html;

    // Load bookmarks for dashboard
    try {
      const bookmarks = await fetchBookmarks();
      if (bookmarks && bookmarks.length > 0) {
        let bmHtml = '<div class="bookmarks-section"><h3>&#9733; 북마크</h3><div class="bookmarks-list">';
        for (const bm of bookmarks) {
          bmHtml += `<div class="bookmark-item" onclick="navigate('#/module/${bm.module_id}')">
            <span class="bookmark-title">${escapeHtml(bm.step_title)}</span>
            <span class="bookmark-module">${escapeHtml(bm.module_title)}</span>
          </div>`;
        }
        bmHtml += '</div></div>';
        app.innerHTML += bmHtml;
      }
    } catch {
      // Ignore bookmark loading errors
    }
  } catch (err) {
    showError(app, "데이터를 불러올 수 없습니다. 네트워크 연결을 확인해주세요.", renderDashboard);
  }
}

// ──────────────────────────────────────────
// Module List
// ──────────────────────────────────────────
async function renderModuleList(stageId) {
  showLoading(app);

  try {
    const [stages, modules] = await Promise.all([
      fetchStages(),
      fetchModules(stageId),
    ]);

    const stage = stages.find((s) => s.id === stageId);
    if (!stage) {
      showError(app, "Stage를 찾을 수 없습니다.", () => navigate("#/"));
      return;
    }

    if (!modules || modules.length === 0) {
      app.innerHTML = `
        <a class="back-link" onclick="navigate('#/')">&larr; 대시보드로</a>
        <h2 class="section-title">Stage ${stage.order_idx}: ${escapeHtml(stage.title)}</h2>
      `;
      showEmpty(app, "모듈을 불러올 수 없습니다.");
      return;
    }

    const pct = stage.total_modules > 0
      ? Math.round((stage.completed_modules / stage.total_modules) * 100)
      : 0;

    let html = `
      <a class="back-link" onclick="navigate('#/')">&larr; 대시보드로</a>
      <h2 class="section-title">Stage ${stage.order_idx}: ${escapeHtml(stage.title)}</h2>
      <p class="section-desc">${escapeHtml(stage.description)}</p>

      <div class="stage-progress-section">
        <div class="progress-label">진도: ${stage.completed_modules} / ${stage.total_modules} 모듈 완료</div>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${pct}%"></div>
        </div>
      </div>

      <div class="module-list">
    `;

    modules.forEach((mod) => {
      const isCompleted = mod.completed_steps >= mod.total_steps && mod.total_steps > 0;
      const isInProgress = mod.completed_steps > 0 && !isCompleted;
      let statusClass = "";
      let statusText = "";

      if (isCompleted) {
        statusClass = "completed";
        statusText = "완료";
      } else if (isInProgress) {
        statusClass = "in-progress";
        statusText = `진행 중 (${mod.completed_steps}/${mod.total_steps})`;
      } else {
        statusClass = "not-started";
        statusText = "미완료";
      }

      const cardClass = `module-card${isCompleted ? " completed" : ""}${isInProgress ? " in-progress" : ""}`;

      html += `
        <div class="${cardClass}" onclick="navigate('#/module/${mod.id}')">
          <div class="module-card-info">
            <div class="module-number">모듈 ${stage.order_idx}-${mod.order_idx}</div>
            <div class="module-title">${escapeHtml(mod.title)}</div>
            <div class="module-desc">${escapeHtml(mod.description)}</div>
          </div>
          <div class="module-status ${statusClass}">
            ${isCompleted ? "&#10003; " : ""}${statusText}
          </div>
        </div>
      `;
    });

    html += `</div>`;
    app.innerHTML = html;
  } catch (err) {
    showError(app, "모듈을 불러올 수 없습니다. 나중에 다시 시도해주세요.", () => renderModuleList(stageId));
  }
}

// ──────────────────────────────────────────
// Learning Screen
// ──────────────────────────────────────────

let bookmarkedSteps = new Set();

// Internal state for the learning screen
let learningState = {
  moduleId: null,
  stageId: null,
  steps: [],
  currentStepIdx: 0,
  stepStates: {},
  elapsedByStepId: {},
  activeStepId: null,
  activeStepStartedAt: null,
  fromAdmin: false,
};

function getStepState(step) {
  if (!learningState.stepStates[step.id]) {
    learningState.stepStates[step.id] = {
      selectedOptionId: null,
      answered: false,
      answerResult: null,
      readingCompleted: Boolean(step.is_completed && step.type === "reading"),
    };
  }
  return learningState.stepStates[step.id];
}

function isStepCompleted(step) {
  const state = getStepState(step);
  if (step.type === "reading") {
    return Boolean(step.is_completed || state.readingCompleted);
  }
  return Boolean(step.is_completed || state.answered);
}

function getMaxReachableStepIdx() {
  const { steps } = learningState;
  if (!steps || steps.length === 0) return 0;
  if (learningState.fromAdmin) return steps.length - 1;

  for (let i = 0; i < steps.length; i++) {
    if (!isStepCompleted(steps[i])) {
      return i;
    }
  }
  return steps.length - 1;
}

function canAccessStepIdx(stepIdx) {
  if (learningState.fromAdmin) return true;
  return stepIdx <= getMaxReachableStepIdx();
}

function persistActiveStepElapsed() {
  if (learningState.activeStepId == null || !learningState.activeStepStartedAt) {
    return;
  }

  const elapsed = Math.round((Date.now() - learningState.activeStepStartedAt) / 1000);
  if (elapsed > 0) {
    const prev = learningState.elapsedByStepId[learningState.activeStepId] || 0;
    learningState.elapsedByStepId[learningState.activeStepId] = prev + elapsed;
  }

  learningState.activeStepStartedAt = null;
}

function startStepTimer(stepId) {
  if (learningState.activeStepId !== stepId) {
    persistActiveStepElapsed();
    learningState.activeStepId = stepId;
    learningState.activeStepStartedAt = Date.now();
    return;
  }

  if (!learningState.activeStepStartedAt) {
    learningState.activeStepStartedAt = Date.now();
  }
}

function clearStepTimer(stepId) {
  delete learningState.elapsedByStepId[stepId];
  if (learningState.activeStepId === stepId) {
    learningState.activeStepId = null;
    learningState.activeStepStartedAt = null;
  }
}

function getStepElapsedSeconds(stepId) {
  if (stepId == null) return 0;
  let elapsed = learningState.elapsedByStepId[stepId] || 0;

  if (learningState.activeStepId === stepId && learningState.activeStepStartedAt) {
    elapsed += Math.round((Date.now() - learningState.activeStepStartedAt) / 1000);
  }

  return elapsed;
}

function goToStep(targetIdx, options = {}) {
  const { confirmPending = true } = options;
  const { steps, currentStepIdx } = learningState;
  if (!steps || steps.length === 0) return;
  if (targetIdx < 0 || targetIdx >= steps.length || targetIdx === currentStepIdx) return;
  if (!canAccessStepIdx(targetIdx)) return;

  const currentStep = steps[currentStepIdx];
  const currentState = getStepState(currentStep);
  const hasPendingSelection = (
    (currentStep.type === "quiz" || currentStep.type === "practice") &&
    !currentState.answered &&
    currentState.selectedOptionId != null
  );

  if (confirmPending && hasPendingSelection) {
    const ok = window.confirm("선택한 답안을 제출하지 않았습니다. 이동하시겠습니까?");
    if (!ok) return;
  }

  persistActiveStepElapsed();
  learningState.currentStepIdx = targetIdx;
  renderCurrentStep();
}

function renderStepTabs() {
  const { steps, currentStepIdx } = learningState;
  if (!steps || steps.length <= 1) return "";

  const maxReachableIdx = getMaxReachableStepIdx();
  let html = `<div class="step-tabs" role="tablist" aria-label="모듈 스텝 이동">`;

  steps.forEach((s, idx) => {
    const isActive = idx === currentStepIdx;
    const isCompleted = isStepCompleted(s);
    const isLocked = !learningState.fromAdmin && idx > maxReachableIdx;
    const classes = [
      "step-tab",
      isActive ? "active" : "",
      isCompleted ? "completed" : "",
      isLocked ? "locked" : "",
    ].filter(Boolean).join(" ");
    const label = isCompleted ? "&#10003;" : `${idx + 1}`;
    const safeTitle = escapeHtml(s.title || `Step ${idx + 1}`);
    html += `
      <button type="button" class="${classes}" data-step-idx="${idx}" title="Step ${idx + 1}: ${safeTitle}" ${isLocked ? "disabled" : ""}>
        <span class="step-tab-index">${label}</span>
      </button>
    `;
  });

  html += `</div>`;
  return html;
}

async function renderLearning(moduleId, isAdmin = false) {
  // If same module and already loaded, just re-render the step
  if (learningState.moduleId === moduleId && learningState.steps.length > 0 && learningState.fromAdmin === isAdmin) {
    renderCurrentStep();
    return;
  }

  showLoading(app);

  try {
    persistActiveStepElapsed();

    const steps = await fetchSteps(moduleId);

    if (!steps || steps.length === 0) {
      showEmpty(app, "학습 콘텐츠가 아직 준비되지 않았습니다.");
      return;
    }

    // Find the first non-completed step to start from, or start at 0
    let startIdx = 0;
    for (let i = 0; i < steps.length; i++) {
      if (!steps[i].is_completed) {
        startIdx = i;
        break;
      }
      if (i === steps.length - 1) {
        startIdx = steps.length - 1;
      }
    }

    // Load bookmarks
    try {
      const bookmarks = await fetchBookmarks();
      bookmarkedSteps = new Set(bookmarks.map(b => b.step_id));
    } catch {
      // Ignore if bookmarks fail to load
    }

    const stepStates = {};
    for (const step of steps) {
      stepStates[step.id] = {
        selectedOptionId: null,
        answered: false,
        answerResult: null,
        readingCompleted: Boolean(step.is_completed && step.type === "reading"),
      };
    }

    learningState = {
      moduleId,
      stageId: null,
      steps,
      currentStepIdx: startIdx,
      stepStates,
      elapsedByStepId: {},
      activeStepId: null,
      activeStepStartedAt: null,
      fromAdmin: isAdmin,
    };

    // Fetch stage info for back-navigation
    try {
      const moduleDetail = await apiCall(`/api/modules/${moduleId}`);
      if (moduleDetail && moduleDetail.stage_id) {
        learningState.stageId = moduleDetail.stage_id;
      }
    } catch {
      // If module detail endpoint fails, try to get stageId from steps or fallback
    }

    renderCurrentStep();
  } catch (err) {
    showError(app, "학습 콘텐츠를 불러올 수 없습니다.", () => renderLearning(moduleId));
  }
}

function renderCurrentStep() {
  const { steps, currentStepIdx, moduleId, stageId } = learningState;
  const step = steps[currentStepIdx];
  const stepState = getStepState(step);
  const totalSteps = steps.length;
  const stepNum = currentStepIdx + 1;
  const pct = Math.round((stepNum / totalSteps) * 100);

  // Track time only while the current step is still being solved.
  const trackTime = step.type === "reading" ? !isStepCompleted(step) : !stepState.answered;
  if (trackTime) {
    startStepTimer(step.id);
  } else if (learningState.activeStepId === step.id) {
    persistActiveStepElapsed();
    learningState.activeStepId = null;
  }

  const backTarget = learningState.fromAdmin
    ? "#/admin/content"
    : (stageId ? `#/stage/${stageId}` : "#/");
  const backLabel = learningState.fromAdmin
    ? "콘텐츠 목록으로"
    : (stageId ? "모듈 목록으로" : "대시보드로");

  const bmClass = bookmarkedSteps.has(step.id) ? "bookmarked" : "";
  const bmStar = bookmarkedSteps.has(step.id) ? "&#9733;" : "&#9734;";

  let html = `
    <a class="back-link" onclick="navigate('${backTarget}')">&larr; ${backLabel}</a>
    <div class="learning-header">
      <div class="step-header-row">
        <div class="step-counter">Step ${stepNum} / ${totalSteps}</div>
        <button class="bookmark-btn ${bmClass}" onclick="handleBookmark(${step.id})" title="북마크">${bmStar}</button>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width: ${pct}%"></div>
      </div>
      <div class="progress-label">${pct}%</div>
      ${renderStepTabs()}
    </div>
  `;

  if (step.type === "reading") {
    html += renderReadingStep(step);
  } else if (step.type === "quiz" || step.type === "practice") {
    html += renderQuizStep(step, stepState);
  }

  app.innerHTML = html;
  attachStepListeners(step);
}

async function handleBookmark(stepId) {
  try {
    const result = await toggleBookmark(stepId);
    if (result.bookmarked) {
      bookmarkedSteps.add(stepId);
    } else {
      bookmarkedSteps.delete(stepId);
    }
    // Update just the bookmark button
    const btn = document.querySelector('.bookmark-btn');
    if (btn) {
      btn.innerHTML = bookmarkedSteps.has(stepId) ? '&#9733;' : '&#9734;';
      btn.classList.toggle('bookmarked', bookmarkedSteps.has(stepId));
    }
  } catch {
    // Silently fail
  }
}

function renderReadingStep(step) {
  const contentHtml = typeof marked !== "undefined" && marked.parse
    ? marked.parse(step.content_md || "")
    : (step.content_md || "").replace(/\n/g, "<br>");
  const isFirst = learningState.currentStepIdx === 0;
  const isLast = learningState.currentStepIdx >= learningState.steps.length - 1;
  const nextLabel = isLast ? "완료" : "다음 &rarr;";

  let html = `
    <div class="reading-card">
      ${contentHtml}
    </div>
  `;

  // Extension card (더 알아보기) for reading steps
  if (step.extension_md) {
    const extensionHtml = typeof marked !== "undefined" && marked.parse
      ? marked.parse(step.extension_md)
      : step.extension_md.replace(/\n/g, "<br>");
    html += `
    <div class="extension-card">
      <button class="extension-toggle" onclick="toggleExtension(this)">
        더 알아보기 ▼
      </button>
      <div class="extension-content" style="display:none">
        ${extensionHtml}
      </div>
    </div>
    `;
  }

  html += `
    <div class="nav-bar">
      <button class="btn btn-secondary" id="prev-btn" ${isFirst ? "disabled" : ""}>&larr; 이전</button>
      <div class="nav-bar-right">
        <button class="btn btn-primary" id="next-btn">${nextLabel}</button>
      </div>
    </div>
  `;

  return html;
}

function renderQuizStep(step, stepState) {
  const { selectedOptionId, answered, answerResult } = stepState;
  const contentHtml = typeof marked !== "undefined" && marked.parse
    ? marked.parse(step.content_md || "")
    : (step.content_md || "").replace(/\n/g, "<br>");
  const isFirst = learningState.currentStepIdx === 0;

  let html = `
    <div class="quiz-card">
      <div class="quiz-question">${contentHtml}</div>
      <div class="options-list">
  `;

  if (step.options && step.options.length > 0) {
    step.options.forEach((opt) => {
      let optClass = "option-btn";

      if (answered && answerResult) {
        // After answer submission
        if (answerResult.correct_option && opt.id === answerResult.correct_option.id) {
          optClass += " correct-reveal";
        }
        if (opt.id === selectedOptionId) {
          if (answerResult.is_correct) {
            optClass += " correct";
          } else {
            optClass += " incorrect";
          }
        }
        optClass += " disabled";
      } else {
        // Before answer
        if (opt.id === selectedOptionId) {
          optClass += " selected";
        }
      }

      html += `
        <button class="${optClass}" data-option-id="${opt.id}" ${answered ? "disabled" : ""}>
          <span class="option-label">${escapeHtml(opt.label)}.</span>
          ${escapeHtml(opt.content)}
        </button>
      `;
    });
  }

  html += `</div>`; // close options-list

  // Show check button or feedback
  if (!answered) {
    html += `
      <div class="nav-bar">
        <button class="btn btn-secondary" id="prev-btn" ${isFirst ? "disabled" : ""}>&larr; 이전</button>
        <div class="nav-bar-right">
          <button class="btn btn-primary" id="check-btn" ${selectedOptionId == null ? "disabled" : ""}>정답 확인</button>
        </div>
      </div>
    `;
  }

  // Feedback area
  if (answered && answerResult) {
    const feedbackClass = answerResult.is_correct ? "success" : "error";
    const feedbackIcon = answerResult.is_correct ? "&#10004;" : "&#10008;";
    const feedbackTitle = answerResult.is_correct ? "정답입니다!" : "오답입니다.";

    const feedbackMd = answerResult.selected_feedback_md || "";
    const feedbackHtml = typeof marked !== "undefined" && marked.parse
      ? marked.parse(feedbackMd)
      : feedbackMd.replace(/\n/g, "<br>");

    let correctInfo = "";
    if (!answerResult.is_correct && answerResult.correct_option) {
      correctInfo = `<p><strong>정답:</strong> ${escapeHtml(answerResult.correct_option.label)}. ${escapeHtml(answerResult.correct_option.content)}</p>`;
    }

    html += `
      <div class="feedback ${feedbackClass}">
        <p><strong>${feedbackIcon} ${feedbackTitle}</strong></p>
        <div class="feedback-md">${feedbackHtml}</div>
        ${correctInfo}
      </div>
    `;

    // Extension card (더 알아보기) for quiz/practice steps — shown only after answering
    if (step.extension_md) {
      const extensionHtml = typeof marked !== "undefined" && marked.parse
        ? marked.parse(step.extension_md)
        : step.extension_md.replace(/\n/g, "<br>");
      html += `
      <div class="extension-card">
        <button class="extension-toggle" onclick="toggleExtension(this)">
          더 알아보기 ▼
        </button>
        <div class="extension-content" style="display:none">
          ${extensionHtml}
        </div>
      </div>
      `;
    }
  }

  html += `</div>`; // close quiz-card

  // Navigation
  if (answered) {
    const isLast = learningState.currentStepIdx >= learningState.steps.length - 1;
    const nextLabel = isLast ? "완료" : "다음 &rarr;";
    html += `
      <div class="nav-bar">
        <button class="btn btn-secondary" id="prev-btn" ${isFirst ? "disabled" : ""}>&larr; 이전</button>
        <div class="nav-bar-right">
          <button class="btn btn-primary" id="next-btn">${nextLabel}</button>
        </div>
      </div>
    `;
  }

  return html;
}

function toggleExtension(btn) {
  const content = btn.nextElementSibling;
  const isHidden = content.style.display === 'none';
  content.style.display = isHidden ? 'block' : 'none';
  btn.textContent = isHidden ? '더 알아보기 ▲' : '더 알아보기 ▼';
}

function attachStepListeners(step) {
  const stepState = getStepState(step);

  const prevBtn = document.getElementById("prev-btn");
  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      goToStep(learningState.currentStepIdx - 1);
    });
  }

  const stepTabs = app.querySelectorAll(".step-tab[data-step-idx]");
  stepTabs.forEach((tab) => {
    if (tab.disabled) return;
    tab.addEventListener("click", () => {
      const targetIdx = parseInt(tab.getAttribute("data-step-idx"));
      goToStep(targetIdx);
    });
  });

  // Option select (quiz/practice before answered)
  if (!stepState.answered) {
    const optionBtns = app.querySelectorAll(".option-btn");
    optionBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const optId = parseInt(btn.getAttribute("data-option-id"));
        stepState.selectedOptionId = optId;
        // Re-render to update selected state
        renderCurrentStep();
      });
    });
  }

  // Check answer button
  const checkBtn = document.getElementById("check-btn");
  if (checkBtn) {
    checkBtn.addEventListener("click", async () => {
      if (stepState.selectedOptionId == null) return;
      checkBtn.disabled = true;
      checkBtn.textContent = "확인 중...";

      try {
        const result = await submitAnswer(step.id, stepState.selectedOptionId);
        stepState.answered = true;
        stepState.answerResult = result;
        step.is_completed = true;
        clearStepTimer(step.id);
        renderCurrentStep();
      } catch (err) {
        checkBtn.disabled = false;
        checkBtn.textContent = "정답 확인";
        alert("답변 제출 중 오류가 발생했습니다. 다시 시도해주세요.");
      }
    });
  }

  // Next button
  const nextBtn = document.getElementById("next-btn");
  if (nextBtn) {
    nextBtn.addEventListener("click", async () => {
      const isLast = learningState.currentStepIdx >= learningState.steps.length - 1;

      // For reading steps, record completion
      if (step.type === "reading" && !isStepCompleted(step)) {
        nextBtn.disabled = true;
        nextBtn.textContent = "처리 중...";
        try {
          await submitAnswer(step.id, null);
          stepState.readingCompleted = true;
          step.is_completed = true;
          clearStepTimer(step.id);
        } catch {
          nextBtn.disabled = false;
          nextBtn.textContent = isLast ? "완료" : "다음 →";
          alert("읽기 완료 처리 중 오류가 발생했습니다. 다시 시도해주세요.");
          return;
        }
      }

      // Move to next step or result
      const { currentStepIdx, steps, moduleId } = learningState;
      if (currentStepIdx < steps.length - 1) {
        goToStep(currentStepIdx + 1, { confirmPending: false });
      } else {
        // Module complete -> result
        persistActiveStepElapsed();
        const prefix = learningState.fromAdmin ? '/admin' : '';
        navigate(`#${prefix}/module/${moduleId}/result`);
      }
    });
  }
}

// ──────────────────────────────────────────
// Result Screen
// ──────────────────────────────────────────
async function renderResult(moduleId, isAdmin = false) {
  showLoading(app);

  try {
    // Get steps to gather quiz stats
    const steps = await fetchSteps(moduleId);

    // Get module detail for stage info
    let moduleDetail = null;
    try {
      moduleDetail = await apiCall(`/api/modules/${moduleId}`);
    } catch {
      // fallback
    }

    const stageId = moduleDetail ? moduleDetail.stage_id : null;

    // Get all modules in the stage to find next module and check if eval module
    let stageModules = [];
    if (stageId) {
      try {
        stageModules = await fetchModules(stageId);
      } catch {
        // fallback
      }
    }

    // Check if this is the last module (evaluation module) in the stage
    const isLastModule = stageModules.length > 0 &&
      stageModules[stageModules.length - 1].id === moduleId;

    if (isLastModule && stageId) {
      // Comprehensive evaluation module
      await renderEvalResult(moduleId, stageId, moduleDetail, steps, isAdmin);
    } else {
      // Normal module completion — find the actual next module
      let nextModuleId = null;
      if (stageModules.length > 0) {
        const currentIdx = stageModules.findIndex((m) => m.id === moduleId);
        if (currentIdx >= 0 && currentIdx < stageModules.length - 1) {
          nextModuleId = stageModules[currentIdx + 1].id;
        }
      }
      renderNormalResult(moduleId, stageId, moduleDetail, steps, nextModuleId, isAdmin);
    }
  } catch (err) {
    showError(app, "결과를 불러올 수 없습니다.", () => renderResult(moduleId, isAdmin));
  }
}

async function renderEvalResult(moduleId, stageId, moduleDetail, steps, isAdmin = false) {
  try {
    const evalResult = await evaluateStage(stageId);

    const passClass = evalResult.passed ? "result-pass" : "result-fail";
    const icon = evalResult.passed ? "&#127942;" : "";
    const title = evalResult.passed ? "축하합니다!" : "아쉽습니다.";
    const subtitle = moduleDetail ? escapeHtml(moduleDetail.title) : `모듈 ${moduleId}`;
    const statusText = evalResult.passed ? "합격" : "불합격";
    const statusIcon = evalResult.passed ? "&#10004;" : "&#10008;";

    let html = `
      <div class="result-container">
        <div class="result-icon">${icon}</div>
        <div class="result-title">${title}</div>
        <div class="result-subtitle">${subtitle}</div>

        <p><strong>${statusIcon} ${statusText}</strong></p>

        <div class="result-score ${passClass}">${Math.round(evalResult.score_pct)}%</div>

        <div class="result-details">
          <p>정답: ${evalResult.correct_answers} / ${evalResult.total_questions} 문항</p>
          <p>합격선: 70%</p>
        </div>
    `;

    if (evalResult.passed) {
      if (evalResult.unlocked_stage_id) {
        // Next stage unlocked
        html += `
        <div class="result-info-box">
          <p>&#127881; 다음 Stage가 해제되었습니다!</p>
          <p>대시보드에서 다음 Stage를 확인하세요.</p>
        </div>
        <div class="result-actions">
          <button class="btn btn-primary" onclick="navigate('${isAdmin ? '#/admin/content' : '#/'}')">대시보드로</button>
        </div>`;
      } else {
        // All stages complete!
        html += `
        <div class="result-info-box result-complete">
          <p>&#127942; 전체 학습을 완료했습니다!</p>
          <p>GEO 세계관 이해부터 Technical GEO 기초 실습까지 모든 과정을 마쳤습니다.</p>
        </div>
        <div class="result-actions">
          <button class="btn btn-primary" onclick="navigate('${isAdmin ? '#/admin/content' : '#/'}')">대시보드로</button>
        </div>`;
      }
    } else {
      html += `
        <div class="result-info-box">
          <p>취약 영역을 복습한 후 다시 도전해보세요.</p>
        </div>
        <div class="result-actions">
          <button class="btn btn-primary" onclick="retryModule(${moduleId}, ${isAdmin})">다시 도전</button>
          <button class="btn btn-secondary" onclick="navigate('${isAdmin ? '#/admin/content' : `#/stage/${stageId}`}')">모듈 목록으로</button>
        </div>
      `;
    }

    html += `</div>`;
    app.innerHTML = html;
  } catch (err) {
    showError(app, "평가 결과를 불러올 수 없습니다.", () => renderResult(moduleId));
  }
}

function renderNormalResult(moduleId, stageId, moduleDetail, steps, nextModuleId, isAdmin = false) {
  const subtitle = moduleDetail ? escapeHtml(moduleDetail.title) : `모듈 ${moduleId}`;

  // Count quiz/practice steps and their correctness
  const quizSteps = steps ? steps.filter((s) => s.type === "quiz" || s.type === "practice") : [];
  const totalSteps = steps ? steps.length : 0;

  let html = `
    <div class="result-container">
      <div class="result-icon">&#127881;</div>
      <div class="result-title">모듈 완료!</div>
      <div class="result-subtitle">${subtitle}</div>

      <div class="result-details">
        <p>&#10004; 학습 완료</p>
        <p>Total ${totalSteps} Steps 모두 완료했습니다!</p>
      </div>

      <div class="result-actions">
  `;

  // Navigate to next module using actual module ID from the list
  if (nextModuleId && stageId) {
    const nPrefix = isAdmin ? '/admin' : '';
    html += `
        <button class="btn btn-primary" onclick="navigate('#${nPrefix}/module/${nextModuleId}')">다음 모듈로</button>
        <button class="btn btn-secondary" onclick="navigate('${isAdmin ? '#/admin/content' : `#/stage/${stageId}`}')">모듈 목록으로</button>
    `;
  } else if (stageId) {
    html += `
        <button class="btn btn-primary" onclick="navigate('${isAdmin ? '#/admin/content' : `#/stage/${stageId}`}')">모듈 목록으로</button>
    `;
  } else {
    html += `
        <button class="btn btn-primary" onclick="navigate('${isAdmin ? '#/admin/content' : '#/'}')">대시보드로</button>
    `;
  }

  html += `
      </div>
    </div>
  `;

  app.innerHTML = html;
}

// ──────────────────────────────────────────
// Retry Module
// ──────────────────────────────────────────
function retryModule(moduleId, isAdmin = false) {
  persistActiveStepElapsed();

  // Reset learning state and reload
  learningState = {
    moduleId: null,
    stageId: null,
    steps: [],
    currentStepIdx: 0,
    stepStates: {},
    elapsedByStepId: {},
    activeStepId: null,
    activeStepStartedAt: null,
    fromAdmin: isAdmin,
  };
  const prefix = isAdmin ? '/admin' : '';
  navigate(`#${prefix}/module/${moduleId}`);
}

// ──────────────────────────────────────────
// Init
// ──────────────────────────────────────────
checkHealth();
router();
