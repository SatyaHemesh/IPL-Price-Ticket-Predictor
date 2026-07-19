/**
 * IPL Ticket Price Predictor — script.js
 * =======================================
 * Handles:
 *  - Theme toggle (dark / light)
 *  - Dynamic stand options based on seat category
 *  - Weekend auto-detection from match date
 *  - Prediction form submission (AJAX)
 *  - Result rendering with animations
 *  - Prediction history (session-backed)
 *  - Download prediction as text
 *  - Hero particle effect
 *  - SRH Demo button
 *  - Input validation
 */

"use strict";

// ──────────────────────────────────────────────────────────────────
// THEME TOGGLE
// ──────────────────────────────────────────────────────────────────
(function () {
  const html   = document.documentElement;
  const toggle = document.getElementById("themeToggle");
  let   theme  = "dark";

  html.setAttribute("data-theme", theme);

  function applyTheme(t) {
    theme = t;
    html.setAttribute("data-theme", t);
    if (toggle) {
      toggle.innerHTML = t === "dark"
        ? '<i class="bi bi-sun-fill"></i>'
        : '<i class="bi bi-moon-fill"></i>';
      toggle.title = `Switch to ${t === "dark" ? "light" : "dark"} mode`;
    }
  }

  applyTheme(theme);

  if (toggle) {
    toggle.addEventListener("click", () => {
      applyTheme(theme === "dark" ? "light" : "dark");
    });
  }
})();


// ──────────────────────────────────────────────────────────────────
// PARTICLES (Hero)
// ──────────────────────────────────────────────────────────────────
(function () {
  const container = document.getElementById("heroParticles");
  if (!container) return;

  const COUNT = 22;
  for (let i = 0; i < COUNT; i++) {
    const p = document.createElement("span");
    p.className = "particle";
    p.style.cssText = [
      `left: ${Math.random() * 100}%`,
      `top: ${30 + Math.random() * 60}%`,
      `animation-duration: ${4 + Math.random() * 6}s`,
      `animation-delay: ${Math.random() * 6}s`,
      `opacity: 0`,
    ].join(";");
    container.appendChild(p);
  }
})();


// ──────────────────────────────────────────────────────────────────
// STAND OPTIONS (dynamic)
// ──────────────────────────────────────────────────────────────────
const seatSelect  = document.getElementById("seat_category");
const standSelect = document.getElementById("stand_type");

function updateStands() {
  if (!seatSelect || !standSelect || typeof STAND_MAP === "undefined") return;
  const cat    = seatSelect.value;
  const stands = STAND_MAP[cat] || ["East", "West", "North", "South"];
  const prev   = standSelect.value;
  standSelect.innerHTML = "";
  stands.forEach(s => {
    const opt = document.createElement("option");
    opt.value = opt.textContent = s;
    if (s === prev) opt.selected = true;
    standSelect.appendChild(opt);
  });
}

if (seatSelect) seatSelect.addEventListener("change", updateStands);
updateStands();


// ──────────────────────────────────────────────────────────────────
// WEEKEND AUTO-DETECT
// ──────────────────────────────────────────────────────────────────
const dateInput    = document.getElementById("match_date");
const weekendChk   = document.getElementById("weekend_check");

function autoWeekend() {
  if (!dateInput || !weekendChk) return;
  const d = new Date(dateInput.value);
  if (!isNaN(d)) {
    const day = d.getUTCDay();
    weekendChk.checked = (day === 0 || day === 6);
  }
}

if (dateInput) {
  dateInput.addEventListener("change", autoWeekend);
  autoWeekend();
}


// ──────────────────────────────────────────────────────────────────
// SRH DEMO BUTTON
// ──────────────────────────────────────────────────────────────────
const srhBtn = document.getElementById("srhDemoBtn");
if (srhBtn) {
  srhBtn.addEventListener("click", () => {
    setVal("match_date",  "2026-06-26");
    setVal("match_time",  "7:30 PM");
    setVal("stadium",     "Rajiv Gandhi International Stadium");
    setVal("home_team",   "SRH");
    setVal("away_team",   "MI");
    setVal("seat_category","VIP");
    setVal("match_type",  "League");
    setVal("weather",     "Sunny");
    setVal("demand_level","High");
    setVal("available_seats", "2000");
    setVal("days_before_match", "0");
    document.getElementById("daysLabel").textContent = "0";
    if (weekendChk) weekendChk.checked = true;
    updateStands();
    autoWeekend();
    document.getElementById("predictionForm").scrollIntoView({ behavior: "smooth" });
  });
}

function setVal(id, val) {
  const el = document.getElementById(id);
  if (el) el.value = val;
}


// ──────────────────────────────────────────────────────────────────
// RESET BUTTON
// ──────────────────────────────────────────────────────────────────
const resetBtn = document.getElementById("resetBtn");
if (resetBtn) {
  resetBtn.addEventListener("click", () => {
    document.getElementById("predictionForm").reset();
    document.getElementById("daysLabel").textContent = "7";
    updateStands();

    // Hide result, show placeholder
    document.getElementById("resultCard").classList.add("d-none");
    document.getElementById("resultError").classList.add("d-none");
    document.getElementById("resultPlaceholder").classList.remove("d-none");
  });
}


// ──────────────────────────────────────────────────────────────────
// FORM SUBMISSION
// ──────────────────────────────────────────────────────────────────
const form       = document.getElementById("predictionForm");
const predictBtn = document.getElementById("predictBtn");
const overlay    = document.getElementById("loadingOverlay");

if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Validate
    const home = document.getElementById("home_team").value;
    const away = document.getElementById("away_team").value;
    if (home === away) {
      showError("Home team and Away team cannot be the same. Please select different teams.");
      return;
    }
    if (!document.getElementById("match_date").value) {
      showError("Please select a match date.");
      return;
    }

    // UI loading state
    setLoadingState(true);

    const formData = new FormData(form);

    // Checkbox values
    formData.set("weekend", document.getElementById("weekend_check").checked ? "Yes" : "No");
    formData.set("holiday", document.getElementById("holiday_check").checked ? "Yes" : "No");

    try {
      const res  = await fetch("/predict", { method: "POST", body: formData });
      const data = await res.json();

      setLoadingState(false);

      if (data.error) {
        showError(data.error);
      } else {
        showResult(data);
        loadHistory();
      }
    } catch (err) {
      setLoadingState(false);
      showError("Network error — make sure the Flask server is running.");
    }
  });
}

function setLoadingState(loading) {
  const textEl    = predictBtn.querySelector(".btn-text");
  const spinnerEl = predictBtn.querySelector(".btn-spinner");

  if (loading) {
    predictBtn.disabled = true;
    textEl.classList.add("d-none");
    spinnerEl.classList.remove("d-none");
    overlay.classList.remove("d-none");
  } else {
    predictBtn.disabled = false;
    textEl.classList.remove("d-none");
    spinnerEl.classList.add("d-none");
    overlay.classList.add("d-none");
  }
}

function showError(msg) {
  document.getElementById("resultPlaceholder").classList.add("d-none");
  document.getElementById("resultCard").classList.add("d-none");

  const errEl = document.getElementById("resultError");
  document.getElementById("errorMessage").textContent = msg;
  errEl.classList.remove("d-none");
}

function showResult(data) {
  document.getElementById("resultPlaceholder").classList.add("d-none");
  document.getElementById("resultError").classList.add("d-none");

  const card = document.getElementById("resultCard");
  card.classList.remove("d-none");
  card.classList.add("fade-in-up");

  // Teams
  const home = document.getElementById("home_team").value;
  const away = document.getElementById("away_team").value;
  document.getElementById("resultTeams").textContent = `${home}  ⚡  ${away}`;

  // Price (animated)
  const priceEl = document.getElementById("resultPrice");
  priceEl.classList.remove("price-pop");
  void priceEl.offsetWidth;  // reflow
  priceEl.classList.add("price-pop");
  animateCountUp(priceEl, 0, data.predicted_price, 900);

  // Range
  document.getElementById("rangeText").textContent =
    `₹${data.confidence_low.toLocaleString("en-IN")} – ₹${data.confidence_high.toLocaleString("en-IN")}`;

  // Meta
  document.getElementById("meta_stadium").textContent    = truncate(data.stadium, 28);
  document.getElementById("meta_seat").textContent       = `${data.seat_category} · ${data.stand_type}`;
  document.getElementById("meta_day").textContent        = data.match_day;
  document.getElementById("meta_match_type").textContent = data.match_type;

  // Confidence bar (model R² as proxy)
  const conf   = 97;
  const fillEl = document.getElementById("confidenceFill");
  const pctEl  = document.getElementById("confidencePct");
  setTimeout(() => { fillEl.style.width = conf + "%"; pctEl.textContent = conf + "%"; }, 100);

  // Scroll result into view on mobile
  if (window.innerWidth < 992) {
    setTimeout(() => card.scrollIntoView({ behavior: "smooth", block: "start" }), 200);
  }
}

function animateCountUp(el, from, to, duration) {
  const start = performance.now();
  function step(now) {
    const pct  = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - pct, 3);
    const val  = Math.round(from + (to - from) * ease);
    el.textContent = "₹" + val.toLocaleString("en-IN");
    if (pct < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function truncate(str, len) {
  return str.length > len ? str.slice(0, len - 1) + "…" : str;
}


// ──────────────────────────────────────────────────────────────────
// HISTORY
// ──────────────────────────────────────────────────────────────────
async function loadHistory() {
  try {
    const res  = await fetch("/history");
    const data = await res.json();
    renderHistory(data.history || []);
  } catch (_) {}
}

function renderHistory(history) {
  const listEl  = document.getElementById("historyList");
  const emptyEl = document.getElementById("historyEmpty");

  if (!history.length) {
    listEl.innerHTML  = "";
    emptyEl.classList.remove("d-none");
    return;
  }

  emptyEl.classList.add("d-none");
  listEl.innerHTML = history.map(h => `
    <div class="col-sm-6 col-md-4 col-lg-3">
      <div class="history-card">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <span class="history-match">${h.home} vs ${h.away}</span>
          <span class="history-badge">${h.seat}</span>
        </div>
        <div class="history-price">₹${h.price.toLocaleString("en-IN")}</div>
        <div class="history-meta">
          <i class="bi bi-geo-alt me-1"></i>${truncate(h.stadium, 22)}<br/>
          <i class="bi bi-calendar2 me-1"></i>${h.date}
          <i class="bi bi-signal ms-2 me-1"></i>${h.demand}
        </div>
        <div class="mt-2" style="font-size:0.7rem; color:var(--color-faint)">
          ${h.timestamp}
        </div>
      </div>
    </div>
  `).join("");
}

// Clear history
const clearBtn = document.getElementById("clearHistoryBtn");
if (clearBtn) {
  clearBtn.addEventListener("click", async () => {
    if (!confirm("Clear all prediction history?")) return;
    await fetch("/clear_history", { method: "POST" });
    renderHistory([]);
  });
}

// Load history on page load
loadHistory();


// ──────────────────────────────────────────────────────────────────
// DOWNLOAD PREDICTION
// ──────────────────────────────────────────────────────────────────
const dlBtn = document.getElementById("downloadBtn");
if (dlBtn) {
  dlBtn.addEventListener("click", () => {
    const price    = document.getElementById("resultPrice").textContent;
    const teams    = document.getElementById("resultTeams").textContent;
    const stadium  = document.getElementById("meta_stadium").textContent;
    const seat     = document.getElementById("meta_seat").textContent;
    const day      = document.getElementById("meta_day").textContent;
    const mtype    = document.getElementById("meta_match_type").textContent;
    const range    = document.getElementById("rangeText").textContent;
    const dateVal  = document.getElementById("match_date")?.value || "";

    const text = [
      "═══════════════════════════════════════",
      "  IPL TICKET PRICE PREDICTION REPORT  ",
      "═══════════════════════════════════════",
      `  Match    : ${teams}`,
      `  Date     : ${dateVal}  (${day})`,
      `  Venue    : ${stadium}`,
      `  Seat     : ${seat}`,
      `  Type     : ${mtype}`,
      "───────────────────────────────────────",
      `  PREDICTED PRICE : ${price}`,
      `  PRICE RANGE     : ${range}`,
      "───────────────────────────────────────",
      `  Model   : Gradient Boosting Regressor`,
      `  R²      : 96.7%`,
      `  Generated: ${new Date().toLocaleString("en-IN")}`,
      "═══════════════════════════════════════",
      "  IPL Ticket Price Predictor",
      "  Vasamshetty Renusri — ML Project",
    ].join("\n");

    const blob = new Blob([text], { type: "text/plain" });
    const a    = document.createElement("a");
    a.href     = URL.createObjectURL(blob);
    a.download = `ipl_prediction_${dateVal}.txt`;
    a.click();
    URL.revokeObjectURL(a.href);
  });
}


// ──────────────────────────────────────────────────────────────────
// SCROLL ANIMATION (Intersection Observer)
// ──────────────────────────────────────────────────────────────────
const observer = new IntersectionObserver(
  (entries) => entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add("fade-in-up");
      observer.unobserve(e.target);
    }
  }),
  { threshold: 0.1 }
);

document.querySelectorAll(".about-step, .stat-pill, .model-table-card")
  .forEach(el => observer.observe(el));
