let pieChart;
let barChart;
let lineChart;

const colors = ["#16a34a", "#65a30d", "#f59e0b", "#0f766e", "#22c55e"];

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("habitForm").addEventListener("submit", handlePrediction);
  handlePrediction(new Event("submit"));
});

async function handlePrediction(event) {
  event.preventDefault();
  const payload = {
    plastic_usage: Number(document.getElementById("plastic_usage").value),
    food_delivery_frequency: Number(document.getElementById("food_delivery_frequency").value),
    shopping_frequency: Number(document.getElementById("shopping_frequency").value),
    recycling_habits: Number(document.getElementById("recycling_habits").value),
    reusable_item_usage: Number(document.getElementById("reusable_item_usage").value)
  };

  const response = await fetch("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  updateDashboard(data);
}

function updateDashboard(data) {
  document.getElementById("wasteLevel").textContent = data.waste_level;
  document.getElementById("wasteScore").textContent = data.waste_score;
  document.getElementById("carbonFootprint").textContent = data.carbon_footprint;
  document.getElementById("sustainabilityScore").textContent = data.sustainability_score;
  document.getElementById("confidenceBadge").textContent = `AI Confidence: ${data.confidence}% (${data.certainty})`;
  document.getElementById("futureRisk").textContent = data.future_risk;

  setProbability("Low", data.probability_low);
  setProbability("Medium", data.probability_medium);
  setProbability("High", data.probability_high);
  renderRecommendations(data.recommendations);
  renderRiskFactors(data.risk_factors);
  renderPieChart(data.composition);
  renderBarChart(data.weekly);
  renderLineChart(data.weekly);
}

function setProbability(name, value) {
  document.getElementById(`prob${name}`).textContent = `${value}%`;
  document.getElementById(`bar${name}`).style.width = `${value}%`;
}

function renderRecommendations(items) {
  const container = document.getElementById("recommendations");
  container.innerHTML = items.map(([text, category]) => `
    <div class="col-md-6">
      <div class="recommendation-card">
        <span class="badge text-bg-success mb-2">${category}</span>
        <p class="mb-0 fw-semibold">${text}</p>
      </div>
    </div>
  `).join("");
}

function renderRiskFactors(items) {
  const container = document.getElementById("riskFactors");
  container.innerHTML = items.map((text) => `
    <div class="col-md-6 col-xl-4">
      <div class="risk-pill"><i class="bi bi-exclamation-triangle text-success me-2"></i>${text}</div>
    </div>
  `).join("");
}

function renderPieChart(composition) {
  const labels = Object.keys(composition);
  const percentages = labels.map(label => composition[label].percentage);
  const amounts = labels.map(label => composition[label].amount);
  const ctx = document.getElementById("pieChart");
  if (pieChart) pieChart.destroy();
  pieChart = new Chart(ctx, {
    type: "pie",
    data: { labels, datasets: [{ data: percentages, backgroundColor: colors }] },
    options: {
      responsive: true,
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) => `${context.label}: ${context.raw}% | ${amounts[context.dataIndex]} kg/month`
          }
        }
      }
    }
  });
  document.getElementById("pieLegend").innerHTML = labels.map((label, index) =>
    `<div><span style="display:inline-block;width:10px;height:10px;background:${colors[index]};border-radius:50%;margin-right:6px"></span>${label}: ${percentages[index]}% (${amounts[index]} kg)</div>`
  ).join("");
}

function renderBarChart(weekly) {
  const ctx = document.getElementById("barChart");
  if (barChart) barChart.destroy();
  barChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: weekly.labels,
      datasets: [
        { label: "Weekly waste generation", data: weekly.waste, backgroundColor: "#16a34a" },
        { label: "Carbon footprint trends", data: weekly.carbon, backgroundColor: "#0f766e" },
        { label: "Recycling performance", data: weekly.recycling, backgroundColor: "#65a30d" },
        { label: "Plastic usage trends", data: weekly.plastic, backgroundColor: "#f59e0b" }
      ]
    },
    options: { responsive: true }
  });
}

function renderLineChart(weekly) {
  const ctx = document.getElementById("lineChart");
  if (lineChart) lineChart.destroy();
  lineChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: weekly.labels,
      datasets: [
        { label: "Weekly eco improvement", data: weekly.eco, borderColor: "#16a34a", tension: 0.35 },
        { label: "Carbon footprint reduction", data: weekly.carbon.map(v => Math.max(0, 40 - v)), borderColor: "#0f766e", tension: 0.35 },
        { label: "Waste reduction trend", data: weekly.waste.map(v => Math.max(0, 100 - v)), borderColor: "#65a30d", tension: 0.35 }
      ]
    },
    options: { responsive: true }
  });
}
