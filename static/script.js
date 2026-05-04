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
    document.getElementById("features-gas-concentration-variation").innerText = json.gas_delta;
    document.getElementById("features-unattended-stove-time").innerText = json.features.stove_time;
  }
}


function initSubmitButton() {
  const checkSubmitBtn = document.getElementById("check-btn-submit");
  console.log(checkSubmitBtn);
  if (!checkSubmitBtn) return;

  checkSubmitBtn.addEventListener("click", async () => {
    console.log("Submitting features...");
    const data = {
      temp: Number(document.getElementById("temperature-input").value),
      gas: Number(document.getElementById("gas-concentration-input").value),
      temp_delta: Number(document.getElementById("temperature-variation-input").value),
      gas_delta: Number(document.getElementById("gas-variation-input").value),
      stove_time: Number(document.getElementById("unattended-stove-time-input").value),

      fire: document.getElementById("fire-status").checked ? 1 : 0,
      stove_on: document.getElementById("stove-status").checked ? 1 : 0,
      human: document.getElementById("people-detected").checked ? 1 : 0
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
  initResetButton();
  initStartPauseButton();
  initServerResetButton();
  initSubmitButton()

  setInterval(refreshData, 2000);
}

document.addEventListener("DOMContentLoaded", initApp);