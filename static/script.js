// ===== TAB =====
function initTabs() {
  const tabs = document.querySelectorAll(".tab");
  const contents = document.querySelectorAll(".tab-content");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const target = tab.dataset.tab;

      tabs.forEach(t => t.classList.remove("active"));
      contents.forEach(c => c.classList.remove("active"));

      tab.classList.add("active");
      document
        .querySelector(`.tab-content[data-content="${target}"]`)
        .classList.add("active");
    });
  });
}

// ===== FILTER =====
function initFilterToggle() {
  const filterBox = document.querySelector(".analysis-filters");
  const header = document.querySelector(".analysis-filter-header");

  header.addEventListener("click", () => {
    filterBox.classList.toggle("collapsed");
  });
}

function ruleResult() {
  document.addEventListener("click", (e) => {
    const item = e.target.closest(".rule-dropdown li");
    if (item) {
      const drop = item.closest(".rule-result");

      drop.querySelector(".selected").innerText = item.innerText;
      drop.dataset.value = item.dataset.value;

      drop.classList.remove("active");
      return;
    }

    const drop = e.target.closest(".rule-result");
    if (drop) {
      const isOpen = drop.classList.contains("active");

      document.querySelectorAll(".rule-result").forEach(d => {
          d.classList.remove("active");
      });

    if (!isOpen) drop.classList.add("active");
    return;
    }

    const deleteBtn = e.target.closest(".rule-delete");
    if (deleteBtn) {
        deleteBtn.closest(".rule").remove();
        return;
    }

    document.querySelectorAll(".rule-result").forEach(d => {
        d.classList.remove("active");
    });
  });
}
function addRule() {
  function createRule() {
    return `
    <li class="rule">
        <label>If</label>
        <input type="text">

        Return
        <div class="rule-result" data-value="0">
            <span class="selected">Safe</span>

            <ul class="rule-dropdown">
                <li data-value="0">Safe</li>
                <li data-value="1">Warning</li>
                <li data-value="2">Danger</li>
            </ul>

            <span class="material-icons-sharp">keyboard_arrow_down</span>
        </div>

        <button class="rule-delete">
            <span class="material-icons-sharp">delete</span>
        </button>
    </li>
    `;
  }
  document.getElementById("rules-btn-add").addEventListener("click", () => {
    const list = document.getElementById("ruleList");
    list.insertAdjacentHTML("beforeend", createRule());
    // ruleResult(); 
  });
}

function submitRules() {
  document.getElementById("rules-btn-submit").addEventListener("click", () => {

    const rules = [];

    document.querySelectorAll(".rule").forEach(rule => {

      const condition = rule.querySelector("input").value.trim();
      const result = rule.querySelector(".rule-result").dataset.value;

      if (condition !== "") {
          rules.push(`"${condition}",${result}`);
      }

    });

    const content = rules.join("\n");

    console.log(content);

    fetch("http://127.0.0.1:5000/save_rules", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({ rules })
    });
  });
}

// ===== REFRESH DATA =====
async function refreshData() {
  const res = await fetch('/data');
  const json = await res.json();

  if (json.prediction) {
    const statusText = document.querySelectorAll(".prediction-status a");
    statusText.forEach(el => 
    {
    switch (json.prediction) {
      case 0:
        el.innerText = "Safe";
        break;
      case 1:
        el.innerText = "Warning";
        break;
      case 2:
        el.innerText = "Danger";
        break;
    }
  });};

  if (json.features && json.timestamp && json.input_mode === "serial") {
    document.getElementById("timestamp").innerText = json.timestamp;
    document.getElementById("gas-concentration").innerText = json.features.gas;
    document.getElementById("temperature").innerText = json.features.temp;
    document.getElementById("fire-status").innerText = json.features.fire;
    document.getElementById("stove-status").innerText = json.features.stove_on;
    document.getElementById("people-detected").innerText = json.features.human;

    document.getElementById("features-gas-concentration").innerText = json.features.gas;
    document.getElementById("features-temperature").innerText = json.features.temp;
    document.getElementById("features-fire-status").innerText = json.features.fire;
    document.getElementById("features-stove-status").innerText = json.features.stove_on;
    document.getElementById("features-people-detected").innerText = json.features.human;
    document.getElementById("features-temperature-variation").innerText = json.features.temp_delta;
    document.getElementById("features-gas-concentration-variation").innerText = json.features.gas_delta;
    document.getElementById("features-stove-time").innerText = json.features.stove_time;
    document.getElementById("features-absence-time").innerText = json.features.absence_time;
  }
}


function initSubmitButton() {
  const checkSubmitBtn = document.getElementById("check-btn-submit");
  if (!checkSubmitBtn) return;

  checkSubmitBtn.addEventListener("click", async () => {
    console.log("Submitting features...");
    const data = {
      temp: Number(document.getElementById("temperature-input").value),
      gas: Number(document.getElementById("gas-concentration-input").value),
      temp_delta: Number(document.getElementById("temperature-variation-input").value),
      gas_delta: Number(document.getElementById("gas-variation-input").value),
      absence_time: Number(document.getElementById("absence-time-input").value),
      stove_time: Number(document.getElementById("stove-time-input").value),

      fire: document.getElementById("fire-status-input").checked ? 1 : 0,
      stove_on: document.getElementById("stove-status-input").checked ? 1 : 0,
      human: document.getElementById("people-detected-input").checked ? 1 : 0
    };

    const res = await fetch("/submit_features", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const result = await res.json();
    console.log(result);
  });
}


// ===== RESET INPUT =====
function initResetButton() {
  const checkResetBtn = document.getElementById("check-btn-clear");

  checkResetBtn.addEventListener("click", () => {
    const inputs = document.querySelectorAll(".check-feature ul li input");

    inputs.forEach(input => {
      if (input.type === "checkbox") {
        input.checked = false;
      } else {
        input.value = "";
      }
    });
  });
}

// ===== START / PAUSE =====
function initStartPauseButton() {
  const sidebarBTNSP = document.getElementById("sidebar-start-pause");

  sidebarBTNSP.addEventListener("click", () => {
    const icon = sidebarBTNSP.querySelector(".material-icons-sharp");

    if (icon.innerText === "play_arrow") {
      icon.innerText = "pause";
      sidebarBTNSP.querySelector("span:last-child").innerText = "Pause";
      fetch("/start");
    } else if (icon.innerText === "pause") {
      icon.innerText = "play_arrow";
      sidebarBTNSP.querySelector("span:last-child").innerText = "Start";
      fetch("/stop");
    }
  });
}

// ===== RESET SERVER =====
function initServerResetButton() {
  const btn = document.getElementById("sidebar-reset");
  if (!btn) return;

  btn.addEventListener("click", () => {
    fetch("/reset");
  });
}

function initApp() {
  initTabs();
  initFilterToggle();
  ruleResult();
  addRule();
  submitRules();
  initResetButton();
  initStartPauseButton();
  initServerResetButton();
  initSubmitButton()

  setInterval(refreshData, 2000);
}

document.addEventListener("DOMContentLoaded", initApp);