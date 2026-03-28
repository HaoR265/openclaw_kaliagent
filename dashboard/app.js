const state = {
  profile: "steady",
  currentView: "mission",
  overview: null,
  tasks: [],
  results: [],
  tools: [],
  recipes: [],
  agents: [],
  missionPlan: null,
};

const els = {
  metricsGrid: document.getElementById("metricsGrid"),
  taskList: document.getElementById("taskList"),
  resultList: document.getElementById("resultList"),
  workerList: document.getElementById("workerList"),
  toolList: document.getElementById("toolList"),
  recipeList: document.getElementById("recipeList"),
  agentWorkbench: document.getElementById("agentWorkbench"),
  publishForm: document.getElementById("publishForm"),
  publishResult: document.getElementById("publishResult"),
  missionForm: document.getElementById("missionForm"),
  missionInput: document.getElementById("missionInput"),
  missionResult: document.getElementById("missionResult"),
  missionSummary: document.getElementById("missionSummary"),
  planList: document.getElementById("planList"),
  serverStatus: document.getElementById("serverStatus"),
  categorySelect: document.getElementById("categorySelect"),
  toolSearch: document.getElementById("toolSearch"),
  specialOnly: document.getElementById("specialOnly"),
  viewButtons: Array.from(document.querySelectorAll(".view-btn")),
  pages: Array.from(document.querySelectorAll(".view-page")),
  modeButtons: Array.from(document.querySelectorAll(".mode-btn")),
  collapseButtons: Array.from(document.querySelectorAll(".collapse-btn")),
};

async function getJson(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

async function postJson(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "request failed");
  return data;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function fmtTime(value) {
  if (!value) return "n/a";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleString();
}

function badge(text, cls = "") {
  return `<span class="badge ${cls}">${escapeHtml(text)}</span>`;
}

function capabilityLabel(capability) {
  return `能力 ${escapeHtml(capability)}`;
}

function agentLabel(agentId) {
  return `代理 ${escapeHtml(agentId)}`;
}

function renderMetrics() {
  const stats = state.overview.stats;
  const states = stats.states;
  const metrics = [
    { label: "Total Tasks", value: stats.total, foot: `最新 ${fmtTime(stats.latest)}` },
    { label: "Queued / Running", value: `${states.queued}/${states.running + states.leased}`, foot: "SQLite/WAL 真源" },
    { label: "Succeeded", value: states.succeeded, foot: `${state.overview.results_count} 条结果镜像` },
    { label: "Dead / Failed", value: `${states.dead_letter}/${states.failed}`, foot: "Steady / Rush 双模式" },
  ];
  els.metricsGrid.innerHTML = metrics
    .map(
      (item) => `
        <article class="metric-card">
          <div class="metric-label">${escapeHtml(item.label)}</div>
          <div class="metric-value">${escapeHtml(item.value)}</div>
          <div class="metric-foot">${escapeHtml(item.foot)}</div>
        </article>
      `,
    )
    .join("");
}

function renderTasks() {
  els.taskList.innerHTML = state.tasks
    .map(
      (task) => `
        <article class="stack-item">
          <div class="item-title">
            <strong>${escapeHtml(task.operation)}</strong>
            <div>${badge(task.profile, task.profile)} ${badge(task.state, task.state)}</div>
          </div>
          <div class="item-sub">${capabilityLabel(task.capability)} / ${agentLabel(task.agent_id)}</div>
          <div class="item-sub">${escapeHtml(task.id.slice(0, 8))} | ${fmtTime(task.created_at)}</div>
          <div class="item-meta">
            ${badge(task.execution_mode)}
            ${task.executor_type ? badge(task.executor_type) : ""}
            ${task.tool_name ? badge(task.tool_name) : ""}
            ${task.interactive ? badge("interactive", "high") : ""}
            ${task.secondary_confirmation ? badge("confirmed", "rush") : ""}
          </div>
        </article>
      `,
    )
    .join("");
}

function renderResults() {
  els.resultList.innerHTML = state.results
    .map((item) => {
      const summary = item.summary || {};
      const message = summary.message || summary.summary || "completed";
      return `
        <article class="stack-item">
          <div class="item-title">
            <strong>${escapeHtml(item.operation)}</strong>
            <div>${badge(item.status, item.status === "failed" ? "failed" : "")}</div>
          </div>
          <div class="item-sub">${capabilityLabel(item.capability)}</div>
          <div class="item-sub">${fmtTime(item.created_at)}</div>
          <div class="item-meta">
            ${badge(message)}
          </div>
        </article>
      `;
    })
    .join("");
}

function renderWorkers() {
  const workerCards = state.overview.workers
    .map(
      (worker) => `
        <article class="stack-item">
          <div class="item-title">
            <strong>${escapeHtml(worker.agent_id)}</strong>
            <div>${badge(worker.status, worker.status === "online" ? "steady" : "failed")}</div>
          </div>
          <div class="item-sub">${escapeHtml(worker.id)}</div>
          <div class="item-meta">${badge(fmtTime(worker.last_heartbeat_at))}</div>
        </article>
      `,
    )
    .join("");

  const logCards = state.overview.logs
    .map(
      (log) => `
        <article class="stack-item">
          <div class="item-title">
            <strong>${escapeHtml(log.category)}</strong>
            <div>${badge(log.exists ? "log" : "none", log.exists ? "steady" : "failed")}</div>
          </div>
          <div class="item-sub">${log.updated_at ? fmtTime(log.updated_at * 1000) : "未找到日志"}</div>
        </article>
      `,
    )
    .join("");

  els.workerList.innerHTML = workerCards + logCards;
}

function renderAgentWorkbench() {
  els.agentWorkbench.innerHTML = state.agents
    .map((item) => {
      const worker = item.worker;
      const counts = item.state_counts || {};
      const recent = (item.recent_tasks || [])
        .map(
          (task) => `
            <div class="mini-row">
              <span>${escapeHtml(task.operation)}</span>
              <span>${badge(task.state, task.state)}</span>
            </div>
          `,
        )
        .join("");

      return `
        <article class="agent-card">
          <div class="item-title">
            <strong>${escapeHtml(item.agent_id)}</strong>
            <div>${badge(worker?.status || "idle", worker?.status === "online" ? "steady" : "failed")}</div>
          </div>
          <div class="item-sub">${capabilityLabel(item.capability)}</div>
          <div class="item-sub">最近心跳 ${fmtTime(worker?.last_heartbeat_at)}</div>
          <div class="item-meta">
            ${badge(`queued:${counts.queued || 0}`)}
            ${badge(`running:${(counts.running || 0) + (counts.leased || 0)}`)}
            ${badge(`ok:${counts.succeeded || 0}`, "steady")}
            ${badge(`fail:${(counts.failed || 0) + (counts.dead_letter || 0)}`, "failed")}
          </div>
          <div class="mini-stack">${recent || '<div class="item-sub">暂无历史任务</div>'}</div>
        </article>
      `;
    })
    .join("");
}

function renderTools() {
  const q = els.toolSearch.value.trim().toLowerCase();
  const onlySpecial = els.specialOnly.checked;
  const tools = state.tools.filter((tool) => {
    if (onlySpecial && !String(tool.category).startsWith("rare-")) return false;
    if (!q) return true;
    const text = [tool.name, tool.category, tool.summary, ...(tool.tags || []), ...(tool.policy_refs || [])]
      .join(" ")
      .toLowerCase();
    return text.includes(q);
  });

  els.toolList.innerHTML = tools
    .map(
      (tool) => `
        <article class="tool-item">
          <div class="item-title">
            <strong>${escapeHtml(tool.name)}</strong>
            <div>${badge(tool.risk_level, tool.risk_level)}</div>
          </div>
          <div class="item-sub">${escapeHtml(tool.catalog)} | ${escapeHtml(tool.category)}</div>
          <div class="item-sub">${escapeHtml(tool.summary)}</div>
          <div class="item-meta">
            ${badge((tool.target_types || []).join(", ") || "n/a")}
            ${tool.interactive ? badge("interactive", "high") : badge("non-interactive", "steady")}
            ${badge((tool.policy_refs || []).join(", "))}
          </div>
        </article>
      `,
    )
    .join("");
}

function renderRecipes() {
  els.recipeList.innerHTML = state.recipes
    .map(
      (recipe) => `
        <article class="recipe-item">
          <div class="item-title">
            <strong>${escapeHtml(recipe.operation)}</strong>
            <div>${badge(recipe.tool_bin)}</div>
          </div>
          <div class="item-sub">${capabilityLabel(recipe.capability)}</div>
          <div class="item-sub">${escapeHtml(recipe.command_template)}</div>
          <div class="item-meta">${(recipe.policy_refs || []).map((p) => badge(p)).join("")}</div>
        </article>
      `,
    )
    .join("");
}

function renderMissionPlan() {
  const plan = state.missionPlan;
  if (!plan) {
    els.missionSummary.innerHTML = "";
    els.planList.innerHTML = "";
    return;
  }

  els.missionSummary.innerHTML = `
    <article class="summary-card">
      <div class="item-title">
        <strong>Command 分析摘要</strong>
        <div>${badge("discussion-first")}</div>
      </div>
      <div class="item-sub">${escapeHtml(plan.summary || "未提供摘要")}</div>
      <div class="item-meta">
        ${(plan.assumptions || []).map((item) => badge(item)).join("")}
      </div>
      ${
        (plan.discussion || []).length
          ? `<div class="mini-stack">${plan.discussion
              .map((item) => `<div class="task-chip">${escapeHtml(item)}</div>`)
              .join("")}</div>`
          : ""
      }
    </article>
  `;

  els.planList.innerHTML = (plan.options || [])
    .map(
      (option, index) => `
        <article class="plan-card">
          <div class="item-title">
            <strong>${escapeHtml(option.title || `方案 ${index + 1}`)}</strong>
            <div>${badge(option.risk || "medium", option.risk || "medium")}</div>
          </div>
          <div class="item-sub">${escapeHtml(option.intent || "")}</div>
          <div class="item-sub">${escapeHtml(option.fit || "")}</div>
          ${option.discussion ? `<div class="item-sub">${escapeHtml(option.discussion)}</div>` : ""}
          <div class="task-chip-list">
            ${(option.tasks || [])
              .map(
                (task) => `
                  <div class="task-chip">
                    <div><strong>${escapeHtml(task.task)}</strong></div>
                    <div>${capabilityLabel(task.category)} / ${agentLabel(`offense-${task.category}`)}</div>
                    <div>${escapeHtml(task.notes || "")}</div>
                  </div>
                `,
              )
              .join("")}
          </div>
          <div class="plan-actions">
            <button class="secondary-btn" type="button" data-plan-publish="${index}">发布此方案</button>
          </div>
        </article>
      `,
    )
    .join("");

  document.querySelectorAll("[data-plan-publish]").forEach((button) => {
    button.addEventListener("click", async () => {
      const index = Number(button.dataset.planPublish);
      await publishPlan(index);
    });
  });
}

function setCurrentView(view) {
  state.currentView = view;
  els.viewButtons.forEach((btn) => btn.classList.toggle("active", btn.dataset.view === view));
  els.pages.forEach((page) => page.classList.toggle("active", page.dataset.viewPage === view));
}

async function publishTask(payload) {
  return postJson("/api/publish", payload);
}

async function publishPlan(index) {
  const option = state.missionPlan?.options?.[index];
  if (!option) return;
  const tasks = option.tasks || [];
  if (!tasks.length) {
    els.missionResult.textContent = "所选方案没有可发布任务";
    return;
  }
  els.missionResult.textContent = `正在发布 ${tasks.length} 条任务...`;
  try {
    for (const task of tasks) {
      await publishTask({
        type: task.type || "task",
        task: task.task,
        category: task.category,
        params: task.params || {},
        executionProfile: state.profile,
      });
    }
    els.missionResult.textContent = `方案已发布: ${escapeHtml(option.title || `方案 ${index + 1}`)}`;
    await refresh();
    setCurrentView("execution");
  } catch (err) {
    els.missionResult.textContent = `方案发布失败: ${err.message}`;
  }
}

function bindCollapses() {
  els.collapseButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.getElementById(button.dataset.collapseTarget);
      target.classList.toggle("collapsed");
      button.textContent = target.classList.contains("collapsed") ? "展开" : "收起";
    });
  });
}

async function refresh() {
  try {
    const [overview, tasks, results, tools, recipes, agents] = await Promise.all([
      getJson("/api/overview"),
      getJson("/api/tasks?limit=14"),
      getJson("/api/results?limit=12"),
      getJson(`/api/tools?profile=${state.profile}`),
      getJson("/api/recipes"),
      getJson("/api/agents"),
    ]);
    state.overview = overview;
    state.tasks = tasks;
    state.results = results;
    state.tools = tools;
    state.recipes = recipes;
    state.agents = agents;
    els.serverStatus.textContent = "dashboard online";

    els.categorySelect.innerHTML = overview.capabilities
      .map((cap) => `<option value="${cap}">${cap}</option>`)
      .join("");
    renderMetrics();
    renderTasks();
    renderResults();
    renderWorkers();
    renderTools();
    renderRecipes();
    renderAgentWorkbench();
    renderMissionPlan();
  } catch (err) {
    els.serverStatus.textContent = `error: ${err.message}`;
  }
}

els.modeButtons.forEach((btn) => {
  btn.addEventListener("click", async () => {
    els.modeButtons.forEach((node) => node.classList.remove("active"));
    btn.classList.add("active");
    state.profile = btn.dataset.profile;
    await refresh();
  });
});

els.viewButtons.forEach((btn) => {
  btn.addEventListener("click", () => setCurrentView(btn.dataset.view));
});

els.toolSearch.addEventListener("input", renderTools);
els.specialOnly.addEventListener("change", renderTools);

els.publishForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(els.publishForm);
  let params = {};
  const raw = document.getElementById("paramsBox").value.trim();
  if (raw) {
    try {
      params = JSON.parse(raw);
    } catch {
      els.publishResult.textContent = "参数 JSON 格式无效";
      return;
    }
  }
  const tool = formData.get("tool");
  const executionMode = formData.get("executionMode");
  if (tool) params.tool = tool;
  if (executionMode) params.executionMode = executionMode;

  const payload = {
    type: formData.get("type"),
    task: formData.get("task"),
    category: formData.get("category"),
    params,
    executionProfile: state.profile,
    interactive: formData.get("interactive") === "on",
    secondaryConfirmation: formData.get("secondaryConfirmation") === "on",
  };

  try {
    const result = await publishTask(payload);
    els.publishResult.textContent = `任务已发布: ${result.event_id}`;
    await refresh();
    setCurrentView("execution");
  } catch (err) {
    els.publishResult.textContent = `发布失败: ${err.message}`;
  }
});

els.missionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = els.missionInput.value.trim();
  if (!text) {
    els.missionResult.textContent = "先输入情报、目标或方向";
    return;
  }
  els.missionResult.textContent = "正在调用 command 分析候选方案...";
  try {
    state.missionPlan = await postJson("/api/mission-plan", {
      text,
      executionProfile: state.profile,
    });
    els.missionResult.textContent = "已生成候选方案，选择一条即可自动发布";
    renderMissionPlan();
  } catch (err) {
    els.missionResult.textContent = `分析失败: ${err.message}`;
  }
});

bindCollapses();
refresh();
setInterval(refresh, 15000);
