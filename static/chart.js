/* ================== STATE ================== */
let rawData = [];
let lastTimestamp = null;
let chart;

/* ================== CSV LOADER ================== */
async function loadCSV(path) {
  const res = await fetch(path + "?t=" + Date.now());
  const text = await res.text();

  const lines = text.trim().split("\n");
  const headers = lines[0].split(",");

  return lines.slice(1).map(line => {
    const values = line.split(",");
    const obj = {};

    headers.forEach((h, i) => {
      obj[h] = (h === "timestamp") ? values[i] : Number(values[i]);
    });

    return obj;
  });
}

/* ================== FIELD MAP ================== */
const fieldMap = {
  temperature: "temp",
  gas: "gas",
  human: "human",
  stove: "stove_on",
  fire: "fire",
  temperature_variation: "temp_delta",
  gas_variation: "gas_delta",
  stove_time: "stove_time",
  label: "label"
};

/* ================== DATASET ================== */
function makeDataset(key, index) {
  return {
    label: key,
    data: rawData.map(r => r[key]),
    borderColor: `hsl(${index * 45},70%,50%)`,
    tension: 0.35,
    yAxisID: "y_" + key,
    pointRadius: 0
  };
}

/* ================== SCALES ================== */
function buildScales(keys) {
  const scales = {
    x: { type: "category" }
  };

  keys.forEach(key => {
    scales["y_" + key] = {
      type: "linear",
      position: "left",
      offset: true,
      grid: { drawOnChartArea: false },
      title: { display: true, text: key }
    };
  });

  return scales;
}

/* ================== CHECKBOX ================== */
const checkboxes = document.querySelectorAll(
  ".analysis-filters input[type='checkbox']"
);

checkboxes.forEach(cb =>
  cb.addEventListener("change", updateChart)
);

function updateChart() {
  const activeKeys = [];

  checkboxes.forEach(cb => {
    if (cb.checked) {
      activeKeys.push(fieldMap[cb.dataset.key]);
    }
  });

  chart.data.datasets = activeKeys.map((key, i) =>
    makeDataset(key, i)
  );

  chart.options.scales = buildScales(activeKeys);
  chart.update();
}

/* ================== INIT CHART ================== */
function initChart() {
  const ctx = document.getElementById("analysisChart");

  chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: rawData.map(r => r.timestamp),
      datasets: []
    },
    options: {
      responsive: true,
      interaction: {
        mode: "index",
        intersect: false
      },
      plugins: {
        legend: { position: "top" }
      },
      scales: {}
    }
  });

  updateChart();
}

/* ================== INCREMENTAL UPDATE ================== */
async function reloadByTime() {
  const data = await loadCSV("../df_train.csv");

  const newRows = lastTimestamp
    ? data.filter(r => r.timestamp > lastTimestamp)
    : data;

  if (!newRows.length) return;

  lastTimestamp = newRows[newRows.length - 1].timestamp;
  rawData.push(...newRows);

  // append labels
  newRows.forEach(r => chart.data.labels.push(r.timestamp));

  // append datasets
  chart.data.datasets.forEach(ds => {
    ds.data.push(...newRows.map(r => r[ds.label]));
  });

  const MAX_POINTS = 300;
  if (chart.data.labels.length > MAX_POINTS) {
    const extra = chart.data.labels.length - MAX_POINTS;
    chart.data.labels.splice(0, extra);
    chart.data.datasets.forEach(d => d.data.splice(0, extra));
    rawData.splice(0, extra);
  }

  chart.update("none");
}

/* ================== START ================== */
(async function start() {
  rawData = await loadCSV("/static/kitchen_data.csv");
  if (rawData.length) {
    lastTimestamp = rawData[rawData.length - 1].timestamp;
  }

  initChart();
  setInterval(reloadByTime, 5000);
})();
