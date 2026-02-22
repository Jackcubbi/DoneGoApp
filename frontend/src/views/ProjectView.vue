<template>
  <div class="dashboard">
    <div class="dashboard__header">
      <div>
        <RouterLink to="/dashboard" class="back-link">
          <ArrowLeftIcon :size="24" />
          <p>Työpöytä</p>
        </RouterLink>
        <h1>{{ project?.name }}</h1>
        <p v-if="project?.project_code" class="text-muted">
          {{ project.project_code }}
        </p>
      </div>
      <div style="display: flex; gap: 0.5rem; align-items: center">
        <RouterLink
          :to="`/projects/${project?.id}/edit`"
          class="btn btn--outline"
        >
          <PencilIcon :size="15" /> Muokkaa
        </RouterLink>
        <RouterLink
          :to="`/reports/new?project_id=${project?.id}`"
          class="btn btn--primary"
        >
          <PlusIcon :size="16" /> Uusi raportti
        </RouterLink>
      </div>
    </div>

    <div v-if="project" class="project-meta-card">
      <div v-if="project.address" class="project-meta-card__item">
        <MapPinIcon :size="14" />
        <span>{{ project.address }}</span>
      </div>
      <div v-if="project.general_company" class="project-meta-card__item">
        <Building2Icon :size="14" />
        <span>{{ project.general_company }}</span>
      </div>
      <div v-if="project.employer" class="project-meta-card__item">
        <UserIcon :size="14" />
        <span>{{ project.employer }}</span>
      </div>
      <div class="project-meta-card__item">
        <CalendarIcon :size="14" />
        <span>{{ formatDate(project.created_at) }}</span>
      </div>
    </div>

    <div v-if="loading" class="loading">Ladataan raportteja…</div>

    <template v-else>
      <!-- Always-visible stats -->
      <div class="dashboard__stats project-stats">
        <div class="stat-card">
          <span class="stat-card__label">Tunnit yhteensä</span>
          <span class="stat-card__value">{{ totalHours }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__label">m² yhteensä</span>
          <span class="stat-card__value">{{ totalArea }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__label">Raportteja</span>
          <span class="stat-card__value">{{ projectReports.length }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__label">Lähetetty</span>
          <span class="stat-card__value">{{ sentCount }}</span>
        </div>
      </div>

      <div v-if="projectReports.length === 0" class="empty-state">
        <div class="empty-state__icon">
          <ClipboardListIcon :size="48" stroke-width="1.2" />
        </div>
        <p>Ei raportteja tässä projektissa.</p>
        <RouterLink
          :to="`/reports/new?project_id=${project?.id}`"
          class="btn btn--primary"
          style="margin-top: 16px"
        >
          <PlusIcon :size="16" /> Luo raportti
        </RouterLink>
      </div>

      <div v-else class="reports-grid">
        <div
          v-for="report in projectReports"
          :key="report.id"
          class="report-card report-card--clickable"
          role="button"
          tabindex="0"
          @click="router.push(`/reports/${report.id}/view`)"
          @keydown.enter="router.push(`/reports/${report.id}/view`)"
        >
          <div class="report-card__header">
            <span class="report-card__week">
              Viikko {{ report.week_number }} / {{ report.year }}
            </span>
            <span
              class="badge"
              :class="{
                'badge--draft': report.status === 'draft',
                'badge--saved': report.status === 'saved',
                'badge--sent': report.status === 'sent',
              }"
              >{{ report.status }}</span
            >
          </div>
          <p class="report-card__entries">
            {{ report.entries.length }} työmerkintä{{
              report.entries.length === 1 ? "y" : "jä"
            }}
          </p>
          <p class="report-card__date text-muted">
            {{ formatDate(report.created_at) }}
          </p>
          <div class="report-card__actions">
            <RouterLink
              :to="`/reports/${report.id}/edit`"
              class="btn btn--sm btn--outline"
              @click.stop
            >
              <PencilIcon :size="13" /> Muokkaa
            </RouterLink>
            <button
              class="btn btn--sm btn--danger"
              :disabled="deletingId === report.id"
              @click.stop="confirmDelete(report.id)"
            >
              <Trash2Icon :size="13" />
              {{ deletingId === report.id ? "…" : "Poista" }}
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>

  <ConfirmModal
    v-model="showDeleteModal"
    title="Poista raportti?"
    message="Tätä toimintoa ei voi kumota. Raportti poistetaan pysyvästi."
    confirm-label="Poista"
    icon="trash"
    variant="danger"
    :loading="deletingId !== null"
    @confirm="handleDelete"
    @cancel="showDeleteModal = false"
  />
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import {
  ArrowLeftIcon,
  PlusIcon,
  PencilIcon,
  Trash2Icon,
  ClipboardListIcon,
  MapPinIcon,
  Building2Icon,
  UserIcon,
  CalendarIcon,
} from "lucide-vue-next";
import { useRoute, useRouter } from "vue-router";
import { useReportsStore } from "../stores/reports";
import { useProjectsStore } from "../stores/projects";
import ConfirmModal from "../components/ConfirmModal.vue";

const route = useRoute();
const router = useRouter();
const reportsStore = useReportsStore();
const projectsStore = useProjectsStore();

const loading = ref(true);
const showDeleteModal = ref(false);
const deletingId = ref(null);
const pendingDeleteId = ref(null);

const projectId = computed(() => parseInt(route.params.id));
const project = computed(() =>
  projectsStore.projects.find((p) => p.id === projectId.value),
);
const projectReports = computed(() =>
  reportsStore.reports.filter((r) => r.project_id === projectId.value),
);

const totalHours = computed(() => {
  const sum = projectReports.value
    .filter((r) => r.status === "saved" || r.status === "sent")
    .reduce(
      (acc, r) =>
        acc +
        r.entries.reduce((a, e) => {
          const v = parseFloat(e.hours);
          return a + (isNaN(v) ? 0 : v);
        }, 0),
      0,
    );
  return sum === 0 ? "0" : String(sum);
});

const totalArea = computed(() => {
  const sum = projectReports.value
    .filter((r) => r.status === "saved" || r.status === "sent")
    .reduce(
      (acc, r) =>
        acc +
        r.entries.reduce((a, e) => {
          const v = parseFloat(e.area);
          return a + (isNaN(v) ? 0 : v);
        }, 0),
      0,
    );
  return sum === 0 ? "0" : String(sum);
});

const sentCount = computed(
  () => projectReports.value.filter((r) => r.status === "sent").length,
);

function confirmDelete(id) {
  pendingDeleteId.value = id;
  showDeleteModal.value = true;
}

async function handleDelete() {
  deletingId.value = pendingDeleteId.value;
  showDeleteModal.value = false;
  try {
    await reportsStore.deleteReport(pendingDeleteId.value);
  } finally {
    deletingId.value = null;
    pendingDeleteId.value = null;
  }
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("fi-FI", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

onMounted(async () => {
  await Promise.all([
    projectsStore.fetchProjects(),
    reportsStore.fetchReports(),
  ]);
  loading.value = false;
});
</script>
