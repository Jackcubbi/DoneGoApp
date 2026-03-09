<template>
  <div class="stats-page">
    <div class="stats-page__header">
      <h1>Statistiikka</h1>
      <p class="text-muted">Yhteenveto kaikista tallennetuista ja lähetetyistä raporteista</p>
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
      <div class="stats-card" v-if="byWeek.length">
        <h2 class="stats-card__title">Tunnit viikottain</h2>
        <div class="stats-card__chart">
          <Bar :data="weekChartData" :options="barOptions" />
        </div>
      </div>
      <div class="stats-card stats-card--empty" v-else>
        <h2 class="stats-card__title">Tunnit viikottain</h2>
        <p class="text-muted">Ei tallennettuja raportteja vielä.</p>
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
            <span class="stats-status-item__count">{{ summary.status_counts?.draft ?? 0 }}</span>
          </div>
          <div class="stats-status-item">
            <span class="badge badge--saved">saved</span>
            <span class="stats-status-item__count">{{ summary.status_counts?.saved ?? 0 }}</span>
          </div>
          <div class="stats-status-item">
            <span class="badge badge--sent">sent</span>
            <span class="stats-status-item__count">{{ summary.status_counts?.sent ?? 0 }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { Bar, Doughnut } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
} from "chart.js";
import api from "../api";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
);

const loading = ref(true);
const summary = ref({});
const byWeek = ref([]);
const byProject = ref([]);
const byWorkcode = ref([]);

// Colour palette matching the app's $primary / design tokens
const PALETTE = [
  "#00c793", "#3b82f6", "#f59e0b", "#ef4444",
  "#a855f7", "#22c55e", "#0ea5e9", "#f97316",
  "#ec4899", "#14b8a6", "#8b5cf6", "#84cc16",
];

const weekChartData = computed(() => ({
  labels: byWeek.value.map((d) => d.label),
  datasets: [
    {
      label: "Tunnit",
      data: byWeek.value.map((d) => d.hours),
      backgroundColor: "#00c793",
      borderRadius: 4,
      borderSkipped: false,
    },
  ],
}));

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

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => ` ${ctx.parsed.y} h`,
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
      ticks: { color: "#495057" },
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

<style scoped>
.stats-page {
  &__header {
    margin-bottom: 1.75rem;

    h1 {
      margin-bottom: 4px;
    }
  }
}

.stats-card {
  background: #fff;
  border: 1px solid #dfe7ef;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  margin-bottom: 1.25rem;

  &__title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #343a40;
    margin-bottom: 1rem;
  }

  &__chart {
    height: 260px;

    &--doughnut {
      height: 280px;
    }
  }

  &--empty {
    p {
      font-size: 0.875rem;
    }
  }
}

.stats-charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
  margin-bottom: 1.25rem;

  .stats-card {
    margin-bottom: 0;
  }

  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
}

.stats-status-row {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.stats-status-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;

  &__count {
    font-size: 1.4rem;
    font-weight: 700;
    color: #343a40;
  }
}
</style>
