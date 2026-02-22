<template>
  <div class="dashboard">
    <div class="dashboard__header">
      <div>
        <h1>Työpöytä</h1>
        <p class="text-muted">Viikko {{ currentWeek }} · {{ currentYear }}</p>
      </div>
      <RouterLink to="/projects/new" class="btn btn--primary">
        <PlusIcon :size="16" /> Uusi projekti
      </RouterLink>
    </div>

    <div v-if="loading" class="loading">Ladataan raportteja…</div>

    <div v-else-if="reports.length === 0" class="empty-state">
      <div class="empty-state__icon">
        <ClipboardListIcon :size="48" stroke-width="1.2" />
      </div>
      <p>Ei projekteja vielä.</p>
      <p class="text-muted">Luo ensimmäinen projekti aloittaaksesi.</p>
      <RouterLink
        to="/projects/new"
        class="btn btn--primary"
        style="margin-top: 16px"
      >
        <PlusIcon :size="16" /> Uusi projekti
      </RouterLink>
    </div>

    <template v-else>
      <div class="dashboard__stats">
        <div class="stat-card">
          <span class="stat-card__label">Tunnit yhteensä</span>
          <span class="stat-card__value">{{ grandTotalHours }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__label">m² yhteensä</span>
          <span class="stat-card__value">{{ grandTotalArea }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-card__label">Raportteja</span>
          <span class="stat-card__value">{{ reports.length }}</span>
        </div>
      </div>

      <!-- Projects section -->
      <div class="section-header">
        <h2>Projektit</h2>
        <RouterLink to="/projects/new" class="btn btn--outline btn--sm">
          <PlusIcon :size="14" /> Uusi projekti
        </RouterLink>
      </div>

      <div v-if="projects.length === 0" class="empty-state empty-state--inline">
        <p class="text-muted">Ei projekteja vielä. Luo ensimmäinen projekti.</p>
      </div>
      <div v-else class="projects-grid">
        <div
          v-for="project in projects"
          :key="project.id"
          class="project-card project-card--clickable"
          role="button"
          tabindex="0"
          @click="router.push(`/projects/${project.id}`)"
          @keydown.enter="router.push(`/projects/${project.id}`)"
        >
          <div class="project-card__header">
            <span class="project-card__name">{{ project.name }}</span>
            <span v-if="project.project_code" class="badge badge--system">
              {{ project.project_code }}
            </span>
          </div>
          <p v-if="project.address" class="project-card__detail">
            {{ project.address }}
          </p>
          <p
            v-if="project.general_company"
            class="project-card__detail text-muted"
          >
            {{ project.general_company }}
          </p>
          <p v-if="project.employer" class="project-card__detail text-muted">
            {{ project.employer }}
          </p>
          <div class="project-card__footer">
            <span class="text-muted" style="font-size: 0.78rem">
              {{ reportCountFor(project.id) }} raportti{{
                reportCountFor(project.id) !== 1 ? "a" : ""
              }}
            </span>
            <button
              class="btn-icon btn-icon--remove"
              title="Poista projekti"
              @click.stop="confirmDeleteProject(project.id)"
            >
              <Trash2Icon :size="13" />
            </button>
          </div>
        </div>
      </div>

      <!-- All reports -->
      <div class="section-header" style="margin-top: 1.75rem">
        <h2>Kaikki raportit</h2>
      </div>
      <div class="reports-grid">
        <div
          v-for="report in reports"
          :key="report.id"
          class="report-card report-card--clickable"
          role="button"
          tabindex="0"
          @click="router.push(`/reports/${report.id}/view`)"
          @keydown.enter="router.push(`/reports/${report.id}/view`)"
        >
          <div class="report-card__header">
            <span class="report-card__week"
              >Viikko {{ report.week_number }} / {{ report.year }}</span
            >
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
          <p
            v-if="projectNameFor(report.project_id)"
            class="report-card__project"
          >
            {{ projectNameFor(report.project_id) }}
          </p>
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

  <ConfirmModal
    v-model="showDeleteProjectModal"
    title="Poista projekti?"
    message="Kaikki projektin raportit jäävät, mutta ne irrotuvat projektista. Tätä ei voi kumota."
    confirm-label="Poista"
    icon="trash"
    variant="danger"
    :loading="deletingProjectId !== null"
    @confirm="handleDeleteProject"
    @cancel="showDeleteProjectModal = false"
  />
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import {
  PlusIcon,
  ClipboardListIcon,
  PencilIcon,
  Trash2Icon,
} from "lucide-vue-next";
import { useRouter } from "vue-router";
import { useReportsStore } from "../stores/reports";
import { useProjectsStore } from "../stores/projects";
import ConfirmModal from "../components/ConfirmModal.vue";

const store = useReportsStore();
const projectsStore = useProjectsStore();
const router = useRouter();
const loading = ref(true);
const deletingId = ref(null);
const pendingDeleteId = ref(null);
const showDeleteModal = ref(false);
const showDeleteProjectModal = ref(false);
const deletingProjectId = ref(null);
const pendingDeleteProjectId = ref(null);

function confirmDelete(id) {
  pendingDeleteId.value = id;
  showDeleteModal.value = true;
}

async function handleDelete() {
  deletingId.value = pendingDeleteId.value;
  showDeleteModal.value = false;
  try {
    await store.deleteReport(pendingDeleteId.value);
  } finally {
    deletingId.value = null;
    pendingDeleteId.value = null;
  }
}

const projects = computed(() => projectsStore.projects);

function projectNameFor(projectId) {
  if (!projectId) return null;
  const p = projectsStore.projects.find((p) => p.id === projectId);
  if (!p) return null;
  return p.project_code ? `${p.project_code} – ${p.name}` : p.name;
}

function reportCountFor(projectId) {
  return store.reports.filter((r) => r.project_id === projectId).length;
}

function confirmDeleteProject(id) {
  pendingDeleteProjectId.value = id;
  showDeleteProjectModal.value = true;
}

async function handleDeleteProject() {
  deletingProjectId.value = pendingDeleteProjectId.value;
  showDeleteProjectModal.value = false;
  try {
    await projectsStore.deleteProject(pendingDeleteProjectId.value);
  } finally {
    deletingProjectId.value = null;
    pendingDeleteProjectId.value = null;
  }
}

const now = new Date();
const currentYear = now.getFullYear();

const currentWeek = computed(() => {
  const d = new Date(
    Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()),
  );
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
});

const reports = computed(() => store.reports);

const grandTotalHours = computed(() => {
  const sum = reports.value
    .filter((r) => r.status === "saved" || r.status === "sent")
    .reduce((acc, r) => {
      return (
        acc +
        r.entries.reduce((a, e) => {
          const v = parseFloat(e.hours);
          return a + (isNaN(v) ? 0 : v);
        }, 0)
      );
    }, 0);
  return sum === 0 ? "0" : String(sum);
});

const grandTotalArea = computed(() => {
  const sum = reports.value
    .filter((r) => r.status === "saved" || r.status === "sent")
    .reduce((acc, r) => {
      return (
        acc +
        r.entries.reduce((a, e) => {
          const v = parseFloat(e.area);
          return a + (isNaN(v) ? 0 : v);
        }, 0)
      );
    }, 0);
  return sum === 0 ? "0" : String(sum);
});

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

onMounted(async () => {
  await Promise.all([store.fetchReports(), projectsStore.fetchProjects()]);
  loading.value = false;
});
</script>
