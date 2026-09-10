// PrivateEye Dashboard Real-Time SSE Client

let activeDomain = "kyc";

function init() {
  setupSSE();
  setupDomainSelector();
  setupTriggerButton();
}

function setupSSE() {
  const evtSource = new EventSource("/api/events");

  evtSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      updateDashboard(data);
    } catch (err) {
      console.error("SSE parse error:", err);
    }
  };

  evtSource.onerror = (err) => {
    console.warn("SSE disconnected, retrying...", err);
  };
}

function setupDomainSelector() {
  const buttons = document.querySelectorAll(".domain-btn");
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeDomain = btn.dataset.domain;
    });
  });
}

function setupTriggerButton() {
  const runBtn = document.getElementById("btn_run_agent");
  if (!runBtn) return;

  runBtn.addEventListener("click", async () => {
    runBtn.disabled = true;
    runBtn.innerHTML = "<span>⏳</span> Launching...";

    try {
      const res = await fetch("/api/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain: activeDomain }),
      });
      const data = await res.json();
      console.log("Agent triggered:", data);
    } catch (err) {
      console.error("Trigger error:", err);
    } finally {
      setTimeout(() => {
        runBtn.disabled = false;
        runBtn.innerHTML = "<span>▶</span> Run Agent";
      }, 3000);
    }
  });
}

function updateDashboard(data) {
  if (!data || !data.step) return;

  // Header meta
  document.getElementById("step_num").innerText = `Step ${data.step}`;
  document.getElementById("current_url").innerText = data.url || "Idle";

  // Images
  const rawImg = document.getElementById("img_raw");
  const rawPlaceholder = document.getElementById("placeholder_raw");
  if (data.raw_image_b64) {
    rawImg.src = `data:image/jpeg;base64,${data.raw_image_b64}`;
    rawImg.style.display = "block";
    if (rawPlaceholder) rawPlaceholder.style.display = "none";
  }

  const sanImg = document.getElementById("img_sanitized");
  const sanPlaceholder = document.getElementById("placeholder_sanitized");
  if (data.sanitized_image_b64) {
    sanImg.src = `data:image/jpeg;base64,${data.sanitized_image_b64}`;
    sanImg.style.display = "block";
    if (sanPlaceholder) sanPlaceholder.style.display = "none";
  }

  // Render bounding box overlays on sanitized view
  renderBoundingBoxes(data.detections || []);

  // Action Panel
  if (data.action) {
    const actBadge = document.getElementById("action_type");
    const actDetail = document.getElementById("action_detail");
    const actReason = document.getElementById("action_reason");

    actBadge.innerText = (data.action.action || "NONE").toUpperCase();
    
    let detailText = "";
    if (data.action.target) {
      const t = data.action.target;
      detailText = `Target: [${t.role || "el"}] ${t.name || t.element_id || ""}`;
    }
    if (data.action.value_ref) {
      detailText += ` ➔ Vault Ref: "${data.action.value_ref}"`;
    }
    actDetail.innerText = detailText || "No target required";
    actReason.innerText = data.action.reason ? `"${data.action.reason}"` : "";
  }

  // Metrics
  const m = data.metrics || {};
  document.getElementById("val_latency").innerText = `${m.total_ms || 0} ms`;
  document.getElementById("val_payload").innerText = `${Math.round((m.payload_bytes || 0) / 1024)} KB`;
  document.getElementById("val_detections").innerText = (data.detections || []).length;
  document.getElementById("val_redactions").innerText = (data.redactions || []).length;

  // Waterfall bars (normalized to ~1000ms max)
  updateWaterfallBar("bar_capture", "val_cap_ms", m.capture_ms || 35);
  updateWaterfallBar("bar_privacy", "val_priv_ms", m.privacy_ms || 18);
  updateWaterfallBar("bar_redact", "val_red_ms", m.redaction_ms || 12);
  updateWaterfallBar("bar_wire", "val_net_ms", m.network_ms || 45);
  updateWaterfallBar("bar_exec", "val_exec_ms", m.execution_ms || 60);

  // Detections Table
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

function renderBoundingBoxes(detections) {
  const overlay = document.getElementById("bbox_overlay");
  if (!overlay) return;
  overlay.innerHTML = "";

  // Viewport assumed 1280x800 for percentage calculation
  const vpWidth = 1280;
  const vpHeight = 800;

  detections.forEach((det) => {
    const box = det.bounding_box;
    if (!box) return;

    const el = document.createElement("div");
    el.className = "bbox-marker";
    el.style.left = `${(box.x / vpWidth) * 100}%`;
    el.style.top = `${(box.y / vpHeight) * 100}%`;
    el.style.width = `${(box.width / vpWidth) * 100}%`;
    el.style.height = `${(box.height / vpHeight) * 100}%`;

    const label = document.createElement("div");
    label.className = "bbox-label";
    label.innerText = `${(det.category || "").toUpperCase()} [${Math.round((det.confidence || 0.9) * 100)}%]`;

    el.appendChild(label);
    overlay.appendChild(el);
  });
}

function renderDetectionsTable(detections) {
  const tbody = document.getElementById("detections_tbody");
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

window.addEventListener("DOMContentLoaded", init);
