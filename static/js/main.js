const palette = ['#00d4ff', '#ff6b35', '#7fff6b', '#ffd700', '#c084fc', '#60a5fa'];
let analyticsCache = null;
let simStops = 1;
let charts = {};

function formatInr(value) {
  return `₹${Math.round(Number(value || 0)).toLocaleString('en-IN')}`;
}

function stopLabel(stop) {
  if (stop === 0) return 'Non-stop';
  if (stop === 1) return '1 Stop';
  return `${stop} Stops`;
}

function formatDelta(value) {
  const absVal = Math.abs(Number(value || 0));
  const sign = value >= 0 ? '+' : '−';
  return `${sign}${formatInr(absVal)}`;
}

async function fetchJson(url, options) {
  const resp = await fetch(url, options);
  if (!resp.ok) {
    throw new Error(`Request failed: ${resp.status}`);
  }
  return resp.json();
}

function replaceSelectOptions(selectId, values, selectedValue) {
  const select = document.getElementById(selectId);
  if (!select) return;
  const selected = String(selectedValue ?? '');
  const options = values.map(v => String(v));
  select.innerHTML = '';
  options.forEach((value) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value;
    option.selected = value === selected;
    select.appendChild(option);
  });
  if (!options.includes(selected) && options.length > 0) {
    select.value = options[0];
  }
}

async function loadOptions() {
  const data = await fetchJson('/api/options');

  replaceSelectOptions('p-airline', data.airlines || [], document.getElementById('p-airline')?.value);
  replaceSelectOptions('sim-airline', data.airlines || [], document.getElementById('sim-airline')?.value);
  replaceSelectOptions('p-src', data.sources || [], document.getElementById('p-src')?.value);
  replaceSelectOptions('p-dst', data.destinations || [], document.getElementById('p-dst')?.value);

  const stopsSelect = document.getElementById('p-stops');
  if (stopsSelect) {
    const selectedStop = String(stopsSelect.value || '1');
    stopsSelect.innerHTML = '';
    (data.stops || []).forEach((stop) => {
      const value = String(stop);
      const option = document.createElement('option');
      option.value = value;
      option.textContent = stopLabel(Number(stop));
      option.selected = value === selectedStop;
      stopsSelect.appendChild(option);
    });
    if (![...(data.stops || [])].map(String).includes(selectedStop) && (data.stops || []).length > 0) {
      stopsSelect.value = String(data.stops[0]);
    }
  }
}

function buildPredictionPayload() {
  const airline = document.getElementById('p-airline').value;
  const source = document.getElementById('p-src').value;
  const destination = document.getElementById('p-dst').value;
  const stops = parseInt(document.getElementById('p-stops').value, 10);
  const journey_day = parseInt(document.getElementById('p-day').value, 10);
  const journey_month = parseInt(document.getElementById('p-month').value, 10);
  const dep_hour = parseInt(document.getElementById('p-hour').value, 10);

  const totalDur = parseInt(document.getElementById('p-dur').value, 10);
  const duration_hour = Math.floor(totalDur / 60);
  const duration_min = totalDur % 60;
  const dep_min = 0;
  const arrival_hour = (dep_hour + duration_hour + Math.floor((dep_min + duration_min) / 60)) % 24;
  const arrival_min = (dep_min + duration_min) % 60;

  return {
    airline,
    source,
    destination,
    stops,
    journey_day,
    journey_month,
    dep_hour,
    dep_min,
    arrival_hour,
    arrival_min,
    duration_hour,
    duration_min,
  };
}

async function runPrediction() {
  if (!document.getElementById('p-airline')) return; // Check if element exists
  const payload = buildPredictionPayload();
  try {
    const data = await fetchJson('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const p = Math.round(data.prediction);
    document.getElementById('result-price').textContent = formatInr(p);
    document.getElementById('result-range').textContent =
      `Expected range: ${formatInr(p - 350)} – ${formatInr(p + 360)}`;
  } catch (error) {
    console.error('Prediction request failed', error);
    document.getElementById('result-price').textContent = 'Unavailable';
    document.getElementById('result-range').textContent = 'Prediction service error.';
  }
}

function updatePrediction() {
  runPrediction();
  updateSim();
}

// Ensure globally accessible
window.updatePrediction = updatePrediction;
window.runPrediction = runPrediction;

function setStop(btn, val) {
  document.querySelectorAll('.sim-toggle-row .toggle-btn').forEach((b) => b.classList.remove('active'));
  btn.classList.add('active');
  simStops = val;
  updateSim();
}

window.setStop = setStop;

function renderSimComparison(rows) {
  const container = document.getElementById('compare-rows');
  if (!container) return;

  if (!rows || rows.length === 0) {
    container.innerHTML = '<div class="compare-row">No data</div>';
    return;
  }
  const min = rows[0].price;
  const max = rows[rows.length - 1].price;
  container.innerHTML = rows.map((row) => {
    let badge = '';
    if (row.price === min) badge = '<span class="compare-delta delta-down">Cheapest</span>';
    if (row.price === max) badge = '<span class="compare-delta delta-up">Priciest</span>';
    const color = row.price === min ? 'var(--accent3)' : row.price === max ? 'var(--accent2)' : 'var(--text)';
    return `<div class="compare-row">
      <span class="compare-airline">${row.airline}</span>
      ${badge}
      <span class="compare-price" style="color:${color}">${formatInr(row.price)}</span>
    </div>`;
  }).join('');
}

function renderSensitivityValue(elementId, delta) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.textContent = formatDelta(delta);
  if (delta > 0) {
    el.style.color = 'var(--accent2)';
  } else if (delta < 0) {
    el.style.color = 'var(--accent3)';
  } else {
    el.style.color = 'var(--muted)';
  }
}

async function updateSim() {
  if (!document.getElementById('sim-airline')) return;
  const payload = {
    airline: document.getElementById('sim-airline').value,
    source: document.getElementById('p-src').value,
    destination: document.getElementById('p-dst').value,
    stops: simStops,
    dep_hour: Number(document.getElementById('sl-hour').value),
    duration: Number(document.getElementById('sl-dur').value),
    days_to_departure: Number(document.getElementById('sl-days').value),
  };

  try {
    const data = await fetchJson('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const baseline = Math.round(data.baseline);
    document.getElementById('sim-price').textContent = formatInr(baseline);
    document.getElementById('sim-delta').textContent =
      `Journey date context: ${String(data.journey_day).padStart(2, '0')}/${String(data.journey_month).padStart(2, '0')}`;
    document.getElementById('sim-delta').style.color = 'var(--muted)';

    renderSimComparison(data.comparison || []);
    renderSensitivityValue('sens-stop', data.sensitivity?.plus_stop ?? 0);
    renderSensitivityValue('sens-dur', data.sensitivity?.plus_60_min ?? 0);
    renderSensitivityValue('sens-days', data.sensitivity?.plus_14_days_early ?? 0);
  } catch (error) {
    console.error('Simulation request failed', error);
    document.getElementById('sim-price').textContent = 'Unavailable';
    document.getElementById('sim-delta').textContent = 'Simulation service error.';
    document.getElementById('sim-delta').style.color = 'var(--accent2)';
  }
}

window.updateSim = updateSim;

function renderTicker(items) {
  const tickerEl = document.getElementById('ticker-inner');
  if (!tickerEl) return;
  if (!items || items.length === 0) {
    tickerEl.innerHTML = '<span class="ticker-item">Ticker data unavailable.</span>';
    return;
  }
  const doubled = [...items, ...items];
  tickerEl.innerHTML = doubled.map((item) => {
    const cls = item.direction === 'up' ? 'up' : 'dn';
    const arrow = item.direction === 'up' ? '▲' : '▼';
    return `<span class="ticker-item">${item.label} <span class="${cls}">${formatInr(item.price)} ${arrow}${item.change_pct}%</span></span>`;
  }).join('');
}

function renderBarChart(canvasId, items, labelField, valueField, title, horizontal = false) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  if (charts[canvasId]) {
    charts[canvasId].destroy();
  }

  if (!items || items.length === 0) return;

  const labels = items.map(item => item[labelField]);
  const data = items.map(item => item[valueField]);
  const bgColors = items.map((_, idx) => palette[idx % palette.length]);

  charts[canvasId] = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: title,
        data: data,
        backgroundColor: bgColors,
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: horizontal ? 'y' : 'x',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { displayColors: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#a0aec0' }
        },
        x: {
          grid: { display: false },
          ticks: { color: '#a0aec0' }
        }
      }
    }
  });
}

function renderRoutes(routes) {
  const tbody = document.getElementById('route-tbody');
  if (!tbody) return;
  if (!routes || routes.length === 0) {
    tbody.innerHTML = '<tr><td colspan="3">No route analytics available.</td></tr>';
    return;
  }
  tbody.innerHTML = routes.map((r) => {
    const badge = r.tag === 'exp'
      ? '<span class="route-badge badge-exp">COSTLY</span>'
      : r.tag === 'cheap'
        ? '<span class="route-badge badge-cheap">CHEAP</span>'
        : '';
    return `<tr>
      <td>${r.route}</td>
      <td style="font-family:'Syne',sans-serif;font-weight:700;">${formatInr(r.price)}</td>
      <td>${badge}</td>
    </tr>`;
  }).join('');
}

function renderMarketShare(items) {
  const canvas = document.getElementById('market-canvas');
  if (!canvas) return;
  const canvasId = 'market-canvas';

  if (charts[canvasId]) {
    charts[canvasId].destroy();
  }

  if (!items || items.length === 0) return;

  const labels = items.map(item => item.name);
  const data = items.map(item => item.share);
  const bgColors = items.map((_, idx) => palette[idx % palette.length]);

  charts[canvasId] = new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: bgColors,
        borderWidth: 0,
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: { position: 'right', labels: { color: '#a0aec0' } }
      }
    }
  });
}

function renderSummary(summary) {
  if (!summary) return;
  const statFlights = document.getElementById('stat-flights');
  const statAirlines = document.getElementById('stat-airlines');
  const statRoutes = document.getElementById('stat-routes');
  const statAvgPrice = document.getElementById('stat-avg-price');

  if (statFlights) statFlights.textContent = Number(summary.flights_analyzed || 0).toLocaleString('en-IN');
  if (statAirlines) statAirlines.textContent = Number(summary.airlines || 0).toLocaleString('en-IN');
  if (statRoutes) statRoutes.textContent = Number(summary.routes || 0).toLocaleString('en-IN');
  if (statAvgPrice) statAvgPrice.textContent = formatInr(summary.avg_price || 0);
}

function renderAnalytics(data) {
  renderSummary(data.summary);
  renderTicker(data.ticker);

  if (data.airline_avg) renderBarChart('airline-canvas', data.airline_avg, 'name', 'val', 'Avg Price (₹)');
  if (data.stops_avg) renderBarChart('stops-canvas', data.stops_avg, 'name', 'val', 'Avg Price (₹)');

  renderRoutes(data.routes);

  if (data.time_slots) renderBarChart('time-canvas', data.time_slots, 'label', 'val', 'Avg Price (₹)');

  renderMarketShare(data.market_share);

  if (data.feature_importance) renderBarChart('fi-canvas', data.feature_importance, 'name', 'pct', 'Importance (%)', true);
}

async function loadAnalytics() {
  const data = await fetchJson('/api/analytics');
  analyticsCache = data;
  renderAnalytics(data);
}

function showPage(id) {
  document.querySelectorAll('.page').forEach((p) => p.classList.remove('active'));
  document.querySelectorAll('.nav-links a').forEach((a) => a.classList.remove('active'));

  const pageTarget = document.getElementById(`page-${id}`);
  const navTarget = document.getElementById(`nav-${id}`);

  if (pageTarget) pageTarget.classList.add('active');
  if (navTarget) navTarget.classList.add('active');

  if (id === 'analytics' && analyticsCache) {
    renderAnalytics(analyticsCache);
  }
  if (id === 'simulator') {
    updateSim();
  }
}

const codeSnippets = {
  fi: `# Calculate Feature Importance from trained ML model
importances = model.feature_importances_
feature_names = encoder.get_feature_names_out()

grouped = {}
for name, importance in zip(feature_names, importances):
    label = normalize_feature_name(str(name))
    grouped[label] = grouped.get(label, 0.0) + float(importance)

# Convert to percentages for top 10 features
total = sum(grouped.values())
result = [
    {"name": name, "pct": round((val / total) * 100, 1)}
    for name, val in sorted(grouped.items(), key=lambda x: x[1], reverse=True)
][:10]`,

  airline: `# Group historical dataset by Airline
# Calculate the mean Price for each group
airline_avg = (
    df.groupby("Airline", as_index=False)["Price"]
    .mean()
    .sort_values("Price", ascending=False)
)`,

  stops: `# Group historical dataset by Total Stops
# Calculate the mean Price for each group
stops_avg = (
    df.groupby("Stops_Int", as_index=False)["Price"]
    .mean()
    .sort_values("Stops_Int")
)`,

  routes: `# Find top expensive and top cheapest flight routes directly from dataset
route_avg = df.groupby("Route", as_index=False)["Price"].mean()
expensive = route_avg.sort_values("Price", ascending=False).head(3)
cheap = route_avg.sort_values("Price", ascending=True).head(2)

# Combine and remove duplicates
routes = pd.concat([expensive, cheap]).drop_duplicates(subset=["Route"])`,

  market: `# Calculate percentage frequency of each Airline in dataset
market_share = (
    df["Airline"]
    .value_counts(normalize=True)
    .reset_index()
)
market_share.columns = ["name", "share"]
market_share["share"] = (market_share["share"] * 100).round(1)`,

  time: `# Map departure hour to Time Slot strings
# Group by Time Segment and calculate mean Price
slot_stats = (
    df.assign(Time_Slot=df["Dep_Hour"].map(slot_for_hour))
    .groupby("Time_Slot", as_index=False)["Price"]
    .mean()
)`
};

function showCode(type) {
  const modal = document.getElementById('code-modal');
  const codeBody = document.getElementById('code-snippet-body');
  if (modal && codeBody && codeSnippets[type]) {
    codeBody.textContent = codeSnippets[type];
    modal.classList.add('active');
  }
}

function closeCode(event) {
  if (event && event.target.id !== 'code-modal' && !event.target.classList.contains('modal-close')) return;
  const modal = document.getElementById('code-modal');
  if (modal) modal.classList.remove('active');
}

window.showPage = showPage;
window.showCode = showCode;
window.closeCode = closeCode;

async function initApp() {
  try {
    await loadOptions();
    await loadAnalytics();
    await runPrediction();
    await updateSim();
  } catch (error) {
    console.error('Initialization error', error);
  }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', initApp);
