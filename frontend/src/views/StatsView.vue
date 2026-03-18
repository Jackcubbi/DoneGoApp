<template>
  <div class="stats-page">
    <div class="stats-page__header">
      <h1>Statistiikka</h1>
      <p class="text-muted">
        Yhteenveto kaikista tallennetuista ja lähetetyistä raporteista
      </p>
    </div>

    <div v-if="loading" class="loading">Ladataan tilastoja…</div>

    <template v-else>
      <!-- Summary cards -->
      <div class="dashboard__stats project-stats" style="margin-bottom: 2rem">
        <div class="stat-card">
          <span class="stat-card__label">Tunnit yhteensä</span>
          <span class="stat-card__value">{{ summary.total_hours ?? 0 }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__label">m² yhteensä</span>
          <span class="stat-card__value">{{ summary.total_area ?? 0 }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__label">Raportteja</span>
          <span class="stat-card__value">{{ summary.report_count ?? 0 }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__label">Projekteja</span>
          <span class="stat-card__value">{{ summary.project_count ?? 0 }}</span>
        </div>
      </div>

      <!-- Hours by week -->
      <div class="stats-card">
        <div class="stats-card__header">
          <h2 class="stats-card__title">Tunnit viikottain</h2>
          <div class="week-filters" v-if="byWeek.length">
            <!-- Mode toggle -->
            <div class="btn-group">
              <button
                :class="['btn--xs', { active: filterMode === 'preset' }]"
                @click="filterMode = 'preset'"
              >
                Pikavalinta
              </button>
              <button
                :class="['btn--xs', { active: filterMode === 'range' }]"
                @click="filterMode = 'range'"
              >
                Aikaväli
              </button>
            </div>

            <!-- Preset controls -->
            <template v-if="filterMode === 'preset'">
              <select v-model="weekYear" class="filter-select">
                <option :value="null">Kaikki vuodet</option>
                <option v-for="y in availableYears" :key="y" :value="y">
                  {{ y }}
                </option>
              </select>
              <div class="btn-group">
                <button
                  v-for="opt in LIMIT_OPTIONS"
                  :key="opt.value"
                  :class="['btn--xs', { active: weekLimit === opt.value }]"
                  @click="weekLimit = opt.value"
                >
                  {{ opt.label }}
                </button>
              </div>
            </template>

            <!-- Range controls -->
            <div v-else class="range-inputs">
              <input
                type="week"
                v-model="rangeFrom"
                class="filter-input-week"
              />
              <span class="range-sep">–</span>
              <input type="week" v-model="rangeTo" class="filter-input-week" />
            </div>

            <!-- Metric toggle (always visible) -->
            <div class="btn-group">
              <button
                :class="['btn--xs', { active: weekMetric === 'hours' }]"
                @click="weekMetric = 'hours'"
              >
                h
              </button>
              <button
                :class="['btn--xs', { active: weekMetric === 'area' }]"
                @click="weekMetric = 'area'"
              >
                m²
              </button>
            </div>
          </div>
        </div>
        <div v-if="processedWeekData.length" class="stats-card__chart">
          <Line :data="weekChartData" :options="lineOptions" />
        </div>
        <p v-else class="text-muted">Ei tallennettuja raportteja vielä.</p>
      </div>

      <div class="stats-charts-row">
        <!-- Hours by project -->
        <div class="stats-card" v-if="byProject.length">
          <h2 class="stats-card__title">Tunnit projekteittain</h2>
          <div class="stats-card__chart stats-card__chart--doughnut">
            <Doughnut :data="projectChartData" :options="doughnutOptions" />
          </div>
        </div>
        <div class="stats-card stats-card--empty" v-else>
          <h2 class="stats-card__title">Tunnit projekteittain</h2>
          <p class="text-muted">Ei projektidataa.</p>
        </div>

        <!-- Hours by work code -->
        <div class="stats-card" v-if="byWorkcode.length">
          <h2 class="stats-card__title">Tunnit työkoodeittain</h2>
          <div class="stats-card__chart stats-card__chart--doughnut">
            <Doughnut :data="workcodeChartData" :options="doughnutOptions" />
          </div>
        </div>
        <div class="stats-card stats-card--empty" v-else>
          <h2 class="stats-card__title">Tunnit työkoodeittain</h2>
          <p class="text-muted">Ei työkoodidataa.</p>
        </div>
      </div>

      <!-- Status breakdown -->
      <div class="stats-card">
        <h2 class="stats-card__title">Raporttien tila</h2>
        <div class="stats-status-row">
          <div class="stats-status-item">
            <span class="badge badge--draft">draft</span>
            <span class="stats-status-item__count">{{
              summary.status_counts?.draft ?? 0
            }}</span>
          </div>
          <div class="stats-status-item">
            <span class="badge badge--saved">saved</span>
            <span class="stats-status-item__count">{{
              summary.status_counts?.saved ?? 0
            }}</span>
          </div>
          <div class="stats-status-item">
            <span class="badge badge--sent">sent</span>
            <span class="stats-status-item__count">{{
              summary.status_counts?.sent ?? 0
            }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from "vue";
import { Line, Doughnut } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  ArcElement,
  Filler,
} from "chart.js";
import api from "../api";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  ArcElement,
  Filler,
);

const loading = ref(true);
const summary = ref({});
const byWeek = ref([]);
const byProject = ref([]);
const byWorkcode = ref([]);

// ── Week chart filters ──────────────────────────────────────
const filterMode = ref("preset"); // 'preset' | 'range'
const weekYear = ref(null);
const weekLimit = ref(5);
const weekMetric = ref("hours");
const rangeFrom = ref("");
const rangeTo = ref("");

// Seed range inputs with the full data span when switching to Aikaväli
watch(filterMode, (mode) => {
  if (mode === "range" && byWeek.value.length) {
    const labels = byWeek.value.map((d) => d.label);
    rangeFrom.value = labels[0].replace("-V", "-W");
    rangeTo.value = labels[labels.length - 1].replace("-V", "-W");
  }
});

const LIMIT_OPTIONS = [
  { label: "2 vk", value: 2 },
  { label: "4 vk", value: 4 },
  { label: "1 kk", value: 5 },
  { label: "1 v", value: 52 },
  { label: "Kaikki", value: 0 },
];

const availableYears = computed(() =>
  [...new Set(byWeek.value.map((d) => parseInt(d.label.split("-")[0])))].sort(
    (a, b) => b - a,
  ),
);

const filteredByWeek = computed(() => {
  if (filterMode.value === "range") {
    const from = rangeFrom.value.replace("-W", "-V");
    const to = rangeTo.value.replace("-W", "-V");
    return byWeek.value.filter(
      (d) => (!from || d.label >= from) && (!to || d.label <= to),
    );
  }
  let data = byWeek.value;
  if (weekYear.value !== null) {
    data = data.filter((d) => d.label.startsWith(String(weekYear.value)));
  }
  return weekLimit.value > 0 ? data.slice(-weekLimit.value) : data;
});

// Convert ISO week label "2026-V13" to "2026-03" (month of the Monday of that week)
function isoWeekToMonth(yearStr, weekStr) {
  const year = parseInt(yearStr);
  const week = parseInt(weekStr);
  const jan4 = new Date(year, 0, 4);
  const dayOfWeek = (jan4.getDay() + 6) % 7; // 0=Mon
  const monday = new Date(jan4);
  monday.setDate(jan4.getDate() - dayOfWeek + (week - 1) * 7);
  return `${monday.getFullYear()}-${String(monday.getMonth() + 1).padStart(2, "0")}`;
}

// Aggregated + relabelled data based on active period selector
const processedWeekData = computed(() => {
  const raw = filteredByWeek.value;

  // Range mode: show raw week labels, no aggregation
  if (filterMode.value === "range") return raw;

  // 1 v or Kaikki → aggregate by year
  if (weekLimit.value === 52 || weekLimit.value === 0) {
    const map = {};
    raw.forEach((d) => {
      const year = d.label.split("-")[0];
      if (!map[year]) map[year] = { label: year, hours: 0, area: 0 };
      map[year].hours += d.hours;
      map[year].area += d.area;
    });
    return Object.values(map).map((v) => ({
      ...v,
      hours: Math.round(v.hours * 100) / 100,
      area: Math.round(v.area * 100) / 100,
    }));
  }

  // 1 kk → aggregate by month (YYYY-MM)
  if (weekLimit.value === 5) {
    const map = {};
    raw.forEach((d) => {
      const [yearStr, weekStr] = d.label.split("-V");
      const month = isoWeekToMonth(yearStr, weekStr);
      if (!map[month]) map[month] = { label: month, hours: 0, area: 0 };
      map[month].hours += d.hours;
      map[month].area += d.area;
    });
    return Object.values(map).map((v) => ({
      ...v,
      hours: Math.round(v.hours * 100) / 100,
      area: Math.round(v.area * 100) / 100,
    }));
  }

  // 2 vk / 4 vk → strip year, show "V13", "V14" …
  return raw.map((d) => ({ ...d, label: d.label.replace(/^\d{4}-/, "") }));
});

// Colour palette matching the app's $primary / design tokens
const PALETTE = [
  "#00c793",
  "#3b82f6",
  "#f59e0b",
  "#ef4444",
  "#a855f7",
  "#22c55e",
  "#0ea5e9",
  "#f97316",
  "#ec4899",
  "#14b8a6",
  "#8b5cf6",
  "#84cc16",
];

const METRIC_CONFIG = {
  hours: {
    label: "Tunnit (h)",
    color: "#00c793",
    bg: "rgba(0, 199, 147, 0.15)",
  },
  area: {
    label: "Pinta-ala (m²)",
    color: "#3b82f6",
    bg: "rgba(59, 130, 246, 0.15)",
  },
};

const weekChartData = computed(() => {
  const cfg = METRIC_CONFIG[weekMetric.value];
  return {
    labels: processedWeekData.value.map((d) => d.label),
    datasets: [
      {
        label: cfg.label,
        data: processedWeekData.value.map((d) => d[weekMetric.value]),
        borderColor: cfg.color,
        backgroundColor: cfg.bg,
        borderWidth: 2.5,
        pointBackgroundColor: cfg.color,
        pointBorderColor: "#fff",
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7,
        tension: 0.35,
        fill: true,
      },
    ],
  };
});

const projectChartData = computed(() => ({
  labels: byProject.value.map((d) => d.label),
  datasets: [
    {
      data: byProject.value.map((d) => d.hours),
      backgroundColor: PALETTE.slice(0, byProject.value.length),
      borderWidth: 0,
    },
  ],
}));

const workcodeChartData = computed(() => ({
  labels: byWorkcode.value.map((d) => d.label),
  datasets: [
    {
      data: byWorkcode.value.map((d) => d.hours),
      backgroundColor: PALETTE.slice(0, byWorkcode.value.length),
      borderWidth: 0,
    },
  ],
}));

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: "index",
    intersect: false,
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) =>
          weekMetric.value === "hours"
            ? ` ${ctx.parsed.y} h`
            : ` ${ctx.parsed.y} m²`,
      },
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { color: "#495057" },
      grid: { color: "#dfe7ef" },
    },
    x: {
      ticks: { color: "#495057", maxRotation: 45 },
      grid: { display: false },
    },
  },
};

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "bottom",
      labels: { color: "#495057", font: { size: 12 }, padding: 12 },
    },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.label}: ${ctx.parsed} h`,
      },
    },
  },
};

onMounted(async () => {
  const [s, w, p, wc] = await Promise.all([
    api.get("/stats/summary"),
    api.get("/stats/by-week"),
    api.get("/stats/by-project"),
    api.get("/stats/by-workcode"),
  ]);
  summary.value = s.data;
  byWeek.value = w.data;
  byProject.value = p.data;
  byWorkcode.value = wc.data;
  loading.value = false;
});
</script>

