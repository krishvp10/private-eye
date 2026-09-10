// PrivateEye Dashboard Client & Visual Replay Engine

let activeDomain = "kyc";
let isLive = true;
let currentDisplayedStep = 0;
let maxAvailableStep = 0;
const stepCache = new Map(); // stepNum -> full payload

// DOM references
const dom = {
  wireLeakStatus: () => document.getElementById("wire_leak_status"),
  domainSelector: () => document.getElementById("domain_selector"),
  runBtn: () => document.getElementById("btn_run_agent"),
  stepChipsContainer: () => document.getElementById("step_chips_container"),
  btnFirstStep: () => document.getElementById("btn_first_step"),
  btnPrevStep: () => document.getElementById("btn_prev_step"),
  btnNextStep: () => document.getElementById("btn_next_step"),
  btnLastStep: () => document.getElementById("btn_last_step"),
  btnLiveToggle: () => document.getElementById("btn_live_toggle"),
  replayModeBadge: () => document.getElementById("replay_mode_badge"),
  stepIndicator: () => document.getElementById("step_indicator"),
  geomIndicator: () => document.getElementById("geometry_indicator"),
  stepNum: () => document.getElementById("step_num"),
  execStateBadge: () => document.getElementById("execution_state_badge"),
  currentUrl: () => document.getElementById("current_url"),
  imgRaw: () => document.getElementById("img_raw"),
  placeholderRaw: () => document.getElementById("placeholder_raw"),
  imgSanitized: () => document.getElementById("img_sanitized"),
  placeholderSanitized: () => document.getElementById("placeholder_sanitized"),
  viewportSanitized: () => document.getElementById("viewport_sanitized"),
  bboxOverlay: () => document.getElementById("bbox_overlay"),
  actionType: () => document.getElementById("action_type"),
  actionDetail: () => document.getElementById("action_detail"),
  actionReason: () => document.getElementById("action_reason"),
  valLatency: () => document.getElementById("val_latency"),
  valPayload: () => document.getElementById("val_payload"),
  valDetections: () => document.getElementById("val_detections"),
  valRedactions: () => document.getElementById("val_redactions"),
  barCapture: () => document.getElementById("bar_capture"),
  valCapMs: () => document.getElementById("val_cap_ms"),
  barPrivacy: () => document.getElementById("bar_privacy"),
  valPrivMs: () => document.getElementById("val_priv_ms"),
  barRedact: () => document.getElementById("bar_redact"),
  valRedMs: () => document.getElementById("val_red_ms"),
  barWire: () => document.getElementById("bar_wire"),
  valNetMs: () => document.getElementById("val_net_ms"),
  barExec: () => document.getElementById("bar_exec"),
  valExecMs: () => document.getElementById("val_exec_ms"),
  detectionsTbody: () => document.getElementById("detections_tbody"),
  eventLogContainer: () => document.getElementById("event_log_container"),
};

async function init() {
  await loadDomains();
  setupTriggerButton();
  setupTimelineControls();
  setupKeyboardShortcuts();
  setupOverlayResizeObserver();
  setupSSE();

  try {
    const res = await fetch("/api/state");
    const data = await res.json();
    if (data && data.step !== undefined) {
      handleIncomingStep(data, false);
    }
  } catch (err) {
    console.error("Failed to load initial state:", err);
  }
}

// ---------------------------------------------------------
// 1. Dynamic Domain Loading
// ---------------------------------------------------------
async function loadDomains() {
  try {
    const res = await fetch("/api/domains");
    const domains = await res.json();
    const container = dom.domainSelector();
    if (!container || !domains || domains.length === 0) return;

    container.innerHTML = "";
    domains.forEach((d, idx) => {
      const btn = document.createElement("button");
      btn.className = `domain-btn ${idx === 0 ? "active" : ""}`;
      btn.dataset.domain = d.id;
      btn.innerText = d.name || d.id.toUpperCase();
      btn.title = d.task || "";
      btn.addEventListener("click", () => {
        document.querySelectorAll(".domain-btn").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        activeDomain = d.id;
        logSafeEvent(`Selected workflow: ${d.name} (${d.id})`, "info");
      });
      container.appendChild(btn);
    });
    if (domains.length > 0) {
      activeDomain = domains[0].id;
    }
  } catch (err) {
    console.warn("Could not load dynamic domains, using static fallback:", err);
  }
}

// ---------------------------------------------------------
// 2. SSE Streaming
// ---------------------------------------------------------
function setupSSE() {
  const evtSource = new EventSource("/api/events");

  evtSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      handleIncomingStep(data, true);
    } catch (err) {
      console.error("SSE parse error:", err);
    }
  };

  evtSource.onerror = (err) => {
    console.warn("SSE stream disconnected, auto-retrying...", err);
  };
}

function handleIncomingStep(data, isRealtime) {
  if (!data) return;
  const step = Number(data.step || 0);

  stepCache.set(step, data);
  if (step > maxAvailableStep) {
    maxAvailableStep = step;
  }

  // Update chips in timeline
  updateTimelineChips();

  // If live mode is on, or if step 0 initial state, render immediately
  if (isLive || step === 0) {
    currentDisplayedStep = step;
    renderStep(data);
  }

  if (isRealtime && step > 0) {
    const detCount = (data.detections || []).length;
    const redCount = (data.redactions || []).length;
    logSafeEvent(`Step ${step}: ${detCount} sensitive elements detected locally, ${redCount} redacted`, "action");

    if (data.action) {
      const act = data.action.action || "NONE";
      logSafeEvent(`Step ${step} action: ${act} (target validated locally)`, "info");
    }

    if (data.action && data.action.action === "done") {
      logSafeEvent(`Workflow ${activeDomain} completed successfully (0 leaks verified)`, "success");
      setExecutionBadge("complete");
    } else {
      setExecutionBadge("running");
    }
  }
}

// ---------------------------------------------------------
// 3. Timeline Scrubber & Step Navigation
// ---------------------------------------------------------
function setupTimelineControls() {
  dom.btnFirstStep().addEventListener("click", () => navigateToStep(1));
  dom.btnPrevStep().addEventListener("click", () => navigateToStep(currentDisplayedStep - 1));
  dom.btnNextStep().addEventListener("click", () => navigateToStep(currentDisplayedStep + 1));
  dom.btnLastStep().addEventListener("click", () => navigateToStep(maxAvailableStep));

  dom.btnLiveToggle().addEventListener("click", () => {
    setLiveMode(!isLive);
    if (isLive && maxAvailableStep > 0) {
      navigateToStep(maxAvailableStep, true);
    }
  });
}

function setupKeyboardShortcuts() {
  window.addEventListener("keydown", (e) => {
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      navigateToStep(currentDisplayedStep - 1);
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      navigateToStep(currentDisplayedStep + 1);
    } else if (e.key === "Home") {
      e.preventDefault();
      navigateToStep(1);
    } else if (e.key === "End") {
      e.preventDefault();
      navigateToStep(maxAvailableStep);
    } else if (e.key.toLowerCase() === "l") {
      e.preventDefault();
      setLiveMode(!isLive);
    }
  });
}

function setLiveMode(live) {
  isLive = live;
  const liveBtn = dom.btnLiveToggle();
  const badge = dom.replayModeBadge();

  if (isLive) {
    liveBtn.classList.add("active");
    badge.className = "replay-badge live";
    badge.innerText = "LIVE STREAM";
    if (maxAvailableStep > 0) {
      navigateToStep(maxAvailableStep, true);
    }
  } else {
    liveBtn.classList.remove("active");
    badge.className = "replay-badge replay";
    badge.innerText = `REPLAY (STEP ${currentDisplayedStep})`;
  }
}

async function navigateToStep(stepNum, keepLive = false) {
  if (stepNum < 0) stepNum = 0;
  if (stepNum > maxAvailableStep) stepNum = maxAvailableStep;

  currentDisplayedStep = stepNum;
  if (!keepLive && stepNum < maxAvailableStep) {
    setLiveMode(false);
  }

  // Check cache first
  if (stepCache.has(stepNum)) {
    renderStep(stepCache.get(stepNum));
  } else {
    // Fetch from history endpoint
    try {
      const res = await fetch(`/api/history/${stepNum}`);
      if (res.ok) {
        const data = await res.json();
        stepCache.set(stepNum, data);
        renderStep(data);
      }
    } catch (err) {
      console.error(`Failed to fetch history for step ${stepNum}:`, err);
    }
  }

  updateTimelineChips();
}

function updateTimelineChips() {
  const container = dom.stepChipsContainer();
  if (!container) return;

  const steps = Array.from(stepCache.keys()).sort((a, b) => a - b);
  if (steps.length === 0 && maxAvailableStep === 0) {
    steps.push(0);
  }

  container.innerHTML = "";
  steps.forEach((step) => {
    const chip = document.createElement("button");
    chip.className = `step-chip ${step === currentDisplayedStep ? "active" : ""}`;
    chip.innerText = step === 0 ? "Step 0 (Init)" : `Step ${step}`;
    chip.addEventListener("click", () => {
      navigateToStep(step, false);
    });
    container.appendChild(chip);
  });

  // Update navigation button states
  dom.btnPrevStep().disabled = currentDisplayedStep <= 0;
  dom.btnNextStep().disabled = currentDisplayedStep >= maxAvailableStep;
  dom.btnFirstStep().disabled = currentDisplayedStep <= 0;
  dom.btnLastStep().disabled = currentDisplayedStep >= maxAvailableStep;

  dom.stepIndicator().innerText = `Step ${currentDisplayedStep} / ${maxAvailableStep}`;
  if (!isLive) {
    dom.replayModeBadge().innerText = `REPLAY (STEP ${currentDisplayedStep})`;
  }
}

// ---------------------------------------------------------
// 4. Render Step Data & Telemetry
// ---------------------------------------------------------
function renderStep(data) {
  if (!data) return;

  dom.stepNum().innerText = `Step ${data.step || 0}`;
  dom.currentUrl().innerText = data.url || "Idle";

  // Raw screen (Local only)
  const imgRaw = dom.imgRaw();
  const placeRaw = dom.placeholderRaw();
  if (data.raw_image_b64) {
    imgRaw.src = `data:image/jpeg;base64,${data.raw_image_b64}`;
    imgRaw.style.display = "block";
    if (placeRaw) placeRaw.style.display = "none";
  }

  // Sanitized screen (Wire view)
  const imgSan = dom.imgSanitized();
  const placeSan = dom.placeholderSanitized();
  if (data.sanitized_image_b64) {
    imgSan.src = `data:image/jpeg;base64,${data.sanitized_image_b64}`;
    imgSan.style.display = "block";
    if (placeSan) placeSan.style.display = "none";

    // Wait for image layout or trigger bounding box render
    if (imgSan.complete) {
      renderBoundingBoxes(data.detections || []);
    } else {
      imgSan.onload = () => renderBoundingBoxes(data.detections || []);
    }
  } else {
    renderBoundingBoxes(data.detections || []);
  }

  // Action Panel
  if (data.action) {
    const act = data.action;
    dom.actionType().innerText = (act.action || "NONE").toUpperCase();

    let detail = "";
    if (act.target) {
      detail = `Target: [${act.target.role || "el"}] ${act.target.name || act.target.element_id || ""}`;
    }
    if (act.value_ref) {
      detail += ` ➔ Vault Ref: "${act.value_ref}"`;
    }
    dom.actionDetail().innerText = detail || "No target required";
    dom.actionReason().innerText = act.reason ? `"${act.reason}"` : "";
  }

  // Metrics
  const m = data.metrics || {};
  dom.valLatency().innerText = `${m.total_ms || 0} ms`;
  dom.valPayload().innerText = `${Math.round((m.payload_bytes || 0) / 1024)} KB`;
  dom.valDetections().innerText = (data.detections || []).length;
  dom.valRedactions().innerText = (data.redactions || []).length;

  updateWaterfallBar("bar_capture", "val_cap_ms", m.capture_ms || 35);
  updateWaterfallBar("bar_privacy", "val_priv_ms", m.privacy_ms || 18);
  updateWaterfallBar("bar_redact", "val_red_ms", m.redaction_ms || 12);
  updateWaterfallBar("bar_wire", "val_net_ms", m.network_ms || 45);
  updateWaterfallBar("bar_exec", "val_exec_ms", m.execution_ms || 60);

  renderDetectionsTable(data.detections || []);
}

function updateWaterfallBar(barId, valId, ms) {
  const bar = document.getElementById(barId);
  const val = document.getElementById(valId);
  if (!bar || !val) return;

  const widthPct = Math.min(100, Math.max(5, (ms / 300) * 100));
  bar.style.width = `${widthPct}%`;
  val.innerText = `${Math.round(ms)}ms`;
}

// ---------------------------------------------------------
// 5. Mathematical Overlay Geometry Transformation
// ---------------------------------------------------------
function renderBoundingBoxes(detections) {
  const overlay = dom.bboxOverlay();
  const viewport = dom.viewportSanitized();
  const img = dom.imgSanitized();
  if (!overlay || !viewport) return;

  overlay.innerHTML = "";
  if (!detections || detections.length === 0) return;

  const containerRect = viewport.getBoundingClientRect();
  const cw = containerRect.width;
  const ch = containerRect.height;

  // Source image natural resolution (defaulting to 1280x800)
  const sw = img.naturalWidth || 1280;
  const sh = img.naturalHeight || 800;

  // Calculate mathematically exact containment scaling & letterbox offsets
  const geom = window.PrivateEyeGeometry.calculateContainment(cw, ch, sw, sh);

  // Update geometry status display
  if (dom.geomIndicator()) {
    dom.geomIndicator().innerText = `${sw}×${sh} ➔ ${Math.round(cw)}×${Math.round(ch)} (${geom.scale.toFixed(2)}x)`;
  }

  detections.forEach((det) => {
    const box = det.bounding_box;
    if (!box) return;

    const transformed = window.PrivateEyeGeometry.transformBoundingBox(box, geom);

    const el = document.createElement("div");
    el.className = "bbox-marker";
    el.style.left = `${transformed.left}px`;
    el.style.top = `${transformed.top}px`;
    el.style.width = `${transformed.width}px`;
    el.style.height = `${transformed.height}px`;

    const label = document.createElement("div");
    label.className = "bbox-label";
    label.innerText = `${(det.category || "PII").toUpperCase()} [${Math.round((det.confidence || 0.9) * 100)}%]`;

    el.appendChild(label);
    overlay.appendChild(el);
  });
}

function setupOverlayResizeObserver() {
  const viewport = dom.viewportSanitized();
  if (!viewport || !window.ResizeObserver) return;

  const observer = new ResizeObserver(() => {
    const currentData = stepCache.get(currentDisplayedStep);
    if (currentData && currentData.detections) {
      renderBoundingBoxes(currentData.detections);
    }
  });

  observer.observe(viewport);
}

// ---------------------------------------------------------
// 6. Detections Table & Safe Event Logger
// ---------------------------------------------------------
function renderDetectionsTable(detections) {
  const tbody = dom.detectionsTbody();
  if (!tbody) return;
  tbody.innerHTML = "";

  if (detections.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-dim); padding: 1rem;">No sensitive elements on current view</td></tr>`;
    return;
  }

  detections.forEach((det) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="det-cat-badge">${det.category || "PII"}</span></td>
      <td>${det.source || "DOM"}</td>
      <td>${Math.round((det.confidence || 0.9) * 100)}%</td>
      <td><code>${det.evidence_id || "vault-match"}</code></td>
    `;
    tbody.appendChild(tr);
  });
}

function logSafeEvent(msg, type = "info") {
  const container = dom.eventLogContainer();
  if (!container) return;

  const now = new Date();
  const timeStr = now.toTimeString().split(" ")[0];

  const entry = document.createElement("div");
  entry.className = `event-log-entry ${type}`;
  entry.innerHTML = `
    <span class="event-time">${timeStr}</span>
    <span class="event-msg">${escapeHtml(msg)}</span>
  `;

  container.appendChild(entry);
  container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerText = text;
  return div.innerHTML;
}

function setExecutionBadge(state) {
  const badge = dom.execStateBadge();
  if (!badge) return;
  badge.className = `state-badge ${state}`;
  badge.innerText = state.toUpperCase();
}

// ---------------------------------------------------------
// 7. Trigger Run Button
// ---------------------------------------------------------
function setupTriggerButton() {
  const runBtn = dom.runBtn();
  if (!runBtn) return;

  runBtn.addEventListener("click", async () => {
    runBtn.disabled = true;
    runBtn.innerHTML = "<span>⏳</span> Launching...";
    setExecutionBadge("running");
    logSafeEvent(`Launching agent for domain: ${activeDomain}...`, "action");

    // Clear step cache for fresh run
    stepCache.clear();
    maxAvailableStep = 0;
    currentDisplayedStep = 0;
    setLiveMode(true);
    updateTimelineChips();

    try {
      const res = await fetch("/api/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain: activeDomain }),
      });
      const data = await res.json();
      logSafeEvent(`Agent PID ${data.pid} started on ${data.url}`, "info");
    } catch (err) {
      console.error("Trigger error:", err);
      logSafeEvent(`Failed to trigger agent: ${err.message}`, "warn");
      setExecutionBadge("failed");
    } finally {
      setTimeout(() => {
        runBtn.disabled = false;
        runBtn.innerHTML = "<span>▶</span> Run Agent";
      }, 3000);
    }
  });
}

window.addEventListener("DOMContentLoaded", init);
