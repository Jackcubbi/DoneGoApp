<template>
  <div class="report-view">
    <div class="report-view__header">
      <RouterLink
        v-if="project"
        :to="`/projects/${project.id}`"
        class="back-link"
      >
        <ArrowLeftIcon />
        {{ project.project_code ? `${project.project_code} – ` : ""
        }}{{ project.name }}
      </RouterLink>

      <h1>
        Viikkoraportti – Viikko {{ report?.week_number }} / {{ report?.year }}
      </h1>
    </div>

    <div v-if="loading" class="loading">Ladataan raporttia…</div>

    <template v-else-if="report">
      <div class="report-view__meta">
        <span
          class="badge"
          :class="{
            'badge--draft': report.status === 'draft',
            'badge--saved': report.status === 'saved',
            'badge--sent': report.status === 'sent',
          }"
          >{{ report.status }}</span
        >
        <span class="text-muted">{{ formatDate(report.created_at) }}</span>
      </div>

      <div v-if="project" class="project-meta-card">
        <div v-if="project.address" class="project-meta-card__item">
          <MapPinIcon :size="14" />
          <span
            ><b>{{ project.address }}</b></span
          >
        </div>
        <div v-if="project.general_company" class="project-meta-card__item">
          <Building2Icon :size="14" />
          <span
            ><b>{{ project.general_company }} </b></span
          >
        </div>
        <div v-if="project.employer" class="project-meta-card__item">
          <UserIcon :size="14" />
          <span
            ><b>{{ project.employer }} </b></span
          >
        </div>
      </div>

      <div class="table-scroll">
        <table class="report-table">
          <thead>
            <tr>
              <th>Päivä</th>
              <th>Tunnit</th>
              <th>m/m²</th>
              <th>Työalue</th>
              <th>Työvaihe/Työnkuvaus</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="day in DAYS" :key="day">
              <tr
                v-for="(entry, rowIdx) in groupedEntries[day]"
                :key="entry.id ?? rowIdx"
              >
                <td
                  v-if="rowIdx === 0"
                  :rowspan="groupedEntries[day].length"
                  class="day-label"
                >
                  <span class="day-label__name">{{ day }}</span>
                  <span class="day-label__date">{{ weekDates[day] }}</span>
                </td>
                <td>{{ entry.hours || "–" }}</td>
                <td>{{ entry.area || "–" }}</td>
                <td>{{ entry.objects || "–" }}</td>
                <td>{{ workCodeLabel(entry.work_code) }}</td>
              </tr>
            </template>
          </tbody>
          <tfoot>
            <tr class="report-table__summary">
              <td class="day-label"><strong>Yhteensä</strong></td>
              <td>
                <strong>{{ totalHours || "–" }}</strong>
              </td>
              <td>
                <strong>{{ totalArea || "–" }}</strong>
              </td>
              <td></td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>

      <div class="report-view__actions">
        <RouterLink :to="`/reports/${report.id}/edit`" class="btn btn--outline">
          <PencilIcon :size="15" /> Muokkaa
        </RouterLink>
        <button class="btn btn--outline" @click="handleDownloadPdf">
          <FileDownIcon :size="15" /> Lataa PDF
        </button>
        <button
          class="btn btn--primary"
          :disabled="sending"
          @click="sendConfirmOpen = true"
        >
          <LoaderIcon v-if="sending" :size="15" class="spin" />
          <SendIcon v-else :size="15" />
          {{
            sending
              ? "Lähetetään…"
              : report.status === "sent"
                ? "Lähetä uudelleen"
                : "Lähetä WhatsApp"
          }}
        </button>
      </div>

      <p v-if="sendError" class="error-msg">{{ sendError }}</p>
    </template>
  </div>

  <ConfirmModal
    v-model="sendConfirmOpen"
    title="Lähetä raportti WhatsAppiin"
    message="Raportti lähetetään WhatsApp-ryhmään. Haluatko jatkaa?"
    confirm-label="Lähetä"
    variant="info"
    icon="send"
    :loading="sending"
    @confirm="handleSend"
    @cancel="sendConfirmOpen = false"
  />
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import {
  ArrowLeftIcon,
  PencilIcon,
  FileDownIcon,
  MapPinIcon,
  Building2Icon,
  UserIcon,
  SendIcon,
  LoaderIcon,
} from "lucide-vue-next";
import ConfirmModal from "../components/ConfirmModal.vue";
import { useRoute } from "vue-router";
import { useReportsStore } from "../stores/reports";
import { useProjectsStore } from "../stores/projects";

const route = useRoute();
const store = useReportsStore();
const projectsStore = useProjectsStore();
const loading = ref(true);
const sendConfirmOpen = ref(false);
const sending = ref(false);
const sendError = ref("");

const DAYS = ["Ma", "Ti", "Ke", "To", "Pe", "La", "Su"];

const reportId = computed(() => parseInt(route.params.id));
const report = computed(() => store.currentReport);
const workCodes = computed(() => store.workCodes);

const weekDates = computed(() => {
  if (!report.value) return {};
  const week = report.value.week_number;
  const year = report.value.year;
  const jan4 = new Date(year, 0, 4);
  const monday = new Date(jan4);
  monday.setDate(jan4.getDate() - ((jan4.getDay() + 6) % 7) + (week - 1) * 7);
  const pad = (n) => String(n).padStart(2, "0");
  return Object.fromEntries(
    DAYS.map((_, i) => {
      const d = new Date(monday);
      d.setDate(monday.getDate() + i);
      return [DAYS[i], `${pad(d.getDate())}.${pad(d.getMonth() + 1)}`];
    }),
  );
});

const project = computed(() => {
  if (!report.value?.project_id) return null;
  return (
    projectsStore.projects.find((p) => p.id === report.value.project_id) ?? null
  );
});

const groupedEntries = computed(() => {
  const map = Object.fromEntries(DAYS.map((d) => [d, []]));
  if (report.value) {
    report.value.entries.forEach((e) => {
      if (map[e.day]) map[e.day].push(e);
    });
  }
  return map;
});

const totalHours = computed(() => {
  if (!report.value) return "";
  const sum = report.value.entries.reduce((acc, e) => {
    const v = parseFloat(e.hours);
    return acc + (isNaN(v) ? 0 : v);
  }, 0);
  return sum === 0 ? "" : String(sum);
});

const totalArea = computed(() => {
  if (!report.value) return "";
  const sum = report.value.entries.reduce((acc, e) => {
    const v = parseFloat(e.area);
    return acc + (isNaN(v) ? 0 : v);
  }, 0);
  return sum === 0 ? "" : String(sum);
});

function workCodeLabel(code) {
  if (!code) return "–";
  const wc = workCodes.value.find((w) => w.code === code);
  return wc ? `${wc.code} – ${wc.description}` : String(code);
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString("fi-FI", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function handleDownloadPdf() {
  store
    .downloadPdf(reportId.value, report.value.week_number, report.value.year)
    .catch(() => {
      alert("PDF-tiedoston lataaminen epäonnistui.");
    });
}

async function handleSend() {
  sending.value = true;
  sendError.value = "";
  try {
    await store.sendReport(reportId.value);
    sendConfirmOpen.value = false;
  } catch (err) {
    sendError.value =
      err.response?.data?.detail ??
      "Lähetys epäonnistui. Tarkista WhatsApp-asetukset.";
  } finally {
    sending.value = false;
  }
}

onMounted(async () => {
  await Promise.all([
    store.fetchReport(reportId.value),
    store.fetchWorkCodes(),
    projectsStore.fetchProjects(),
  ]);
  loading.value = false;
});
</script>
