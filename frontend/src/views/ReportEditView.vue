<template>
  <div class="report-edit">
    <div class="report-edit__header">
      <RouterLink
        v-if="project"
        :to="`/projects/${project.id}`"
        class="back-link"
      >
        <ArrowLeftIcon />
        {{ project.project_code ? `${project.project_code} – ` : ""
        }}{{ project.name }}
      </RouterLink>
      <RouterLink v-else to="/dashboard" class="back-link">
        <ArrowLeftIcon />
        <p>Työpöytä</p>
      </RouterLink>
      <h1>
        {{
          isNew
            ? "Uusi raportti"
            : `Muokkaa raporttia – Viikko ${form.week_number} / ${form.year}`
        }}
      </h1>
    </div>

    <div class="report-edit__meta">
      <div class="form-group">
        <label>Viikko </label>
        <input
          v-model.number="form.week_number"
          type="number"
          min="1"
          max="53"
        />
      </div>
      <div class="form-group">
        <label>Vuosi</label>
        <input v-model.number="form.year" type="number" min="2020" max="2100" />
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
            <th></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="day in DAYS" :key="day">
            <tr
              v-for="({ entry, idx }, rowIdx) in groupedEntries[day]"
              :key="idx"
            >
              <td
                v-if="rowIdx === 0"
                :rowspan="groupedEntries[day].length"
                class="day-label"
              >
                <span class="day-label__name">{{ day }}</span>
                <span class="day-label__date">{{ weekDates[day] }}</span>
              </td>
              <td>
                <input
                  v-model="entry.hours"
                  type="text"
                  class="input-sm"
                  placeholder="8"
                />
              </td>
              <td>
                <input v-model="entry.area" type="text" class="input-sm" />
              </td>
              <td>
                <input v-model="entry.objects" type="text" class="input-sm" />
              </td>
              <td>
                <select v-model.number="entry.work_code" class="input-sm">
                  <option :value="null">–</option>
                  <option v-for="wc in workCodes" :key="wc.id" :value="wc.code">
                    {{ wc.code }} – {{ wc.description }}
                  </option>
                </select>
              </td>
              <td class="row-actions">
                <button
                  v-if="rowIdx === groupedEntries[day].length - 1"
                  type="button"
                  class="btn-icon btn-icon--add"
                  title="Lisää rivi"
                  @click="addRowForDay(day)"
                >
                  <PlusIcon :size="13" />
                </button>
                <button
                  v-if="groupedEntries[day].length > 1"
                  type="button"
                  class="btn-icon btn-icon--remove"
                  title="Poista rivi"
                  @click="removeRow(idx)"
                >
                  <XIcon :size="13" />
                </button>
              </td>
            </tr>
          </template>
        </tbody>
        <tfoot>
          <tr class="report-table__summary">
            <td class="day-label"><strong>Yhteensä</strong></td>
            <td>
              <input
                :value="totalHours"
                type="text"
                class="input-sm input-sm--summary"
                readonly
              />
            </td>
            <td>
              <input
                :value="totalArea"
                type="text"
                class="input-sm input-sm--summary"
                readonly
              />
            </td>
            <td></td>
            <td></td>
            <td></td>
          </tr>
        </tfoot>
      </table>
    </div>

    <p v-if="error" class="error-msg">{{ error }}</p>
    <p v-if="successMsg" class="success-msg">{{ successMsg }}</p>

    <div class="report-edit__actions">
      <button
        class="btn btn--outline"
        :disabled="saving"
        @click="showSaveModal = true"
      >
        <SaveIcon :size="15" /> {{ saving ? "Tallennetaan…" : "Tallenna" }}
      </button>
      <button v-if="!isNew" class="btn btn--outline" @click="handleDownloadPdf">
        <FileDownIcon :size="15" /> Lataa PDF
      </button>
      <button
        v-if="!isNew"
        class="btn btn--primary"
        :disabled="sending"
        @click="showSendModal = true"
      >
        <SendIcon :size="15" />
        {{ sending ? "Lähetetään…" : "Lähetä raportti" }}
      </button>
    </div>
  </div>

  <ConfirmModal
    v-model="showSaveModal"
    title="Tallenna raportti?"
    message="Haluatko tallentaa raporttin muutokset?"
    confirm-label="Tallenna"
    icon="save"
    variant="info"
    :loading="saving"
    @confirm="handleSave"
    @cancel="showSaveModal = false"
  />

  <ConfirmModal
    v-model="showSendModal"
    title="Lähetä raportti?"
    message="Raportti lähetetään WhatsApp-viestillä. Tätä ei voi peruuttaa."
    confirm-label="Lähetä"
    icon="send"
    variant="success"
    :loading="sending"
    @confirm="handleSend"
    @cancel="showSendModal = false"
  />
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import {
  SaveIcon,
  FileDownIcon,
  SendIcon,
  ArrowLeftIcon,
  PlusIcon,
  XIcon,
} from "lucide-vue-next";
import { useRoute, useRouter, onBeforeRouteLeave } from "vue-router";
import { useReportsStore } from "../stores/reports";
import { useProjectsStore } from "../stores/projects";
import ConfirmModal from "../components/ConfirmModal.vue";

const DAYS = ["Ma", "Ti", "Ke", "To", "Pe", "La", "Su"];

function getISOWeek(date) {
  const d = new Date(
    Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()),
  );
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
}

function emptyEntries() {
  return DAYS.map((day) => ({
    day,
    hours: null,
    area: null,
    objects: null,
    description: null,
    work_code: null,
  }));
}

const now = new Date();
const route = useRoute();
const router = useRouter();
const store = useReportsStore();
const projectsStore = useProjectsStore();

const isNew = computed(() => route.path === "/reports/new");
const reportId = computed(() =>
  route.params.id ? parseInt(route.params.id) : null,
);

const form = ref({
  week_number: getISOWeek(now),
  year: now.getFullYear(),
  project_id: null,
  entries: emptyEntries(),
});

const workCodes = computed(() => store.workCodes);
const projects = computed(() => projectsStore.projects);
const project = computed(
  () => projects.value.find((p) => p.id === form.value.project_id) ?? null,
);

// Map day names to actual dates for the selected week/year
const weekDates = computed(() => {
  const week = form.value.week_number;
  const year = form.value.year;
  // Find Monday of the ISO week: Jan 4 is always in week 1
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

const groupedEntries = computed(() => {
  const map = Object.fromEntries(DAYS.map((d) => [d, []]));
  form.value.entries.forEach((entry, idx) => {
    if (map[entry.day]) map[entry.day].push({ entry, idx });
  });
  return map;
});

function addRowForDay(day) {
  form.value.entries.push({
    day,
    hours: null,
    area: null,
    objects: null,
    description: null,
    work_code: null,
  });
}

function removeRow(idx) {
  form.value.entries.splice(idx, 1);
}

const totalHours = computed(() => {
  const sum = form.value.entries.reduce((acc, e) => {
    const v = parseFloat(e.hours);
    return acc + (isNaN(v) ? 0 : v);
  }, 0);
  return sum === 0 ? "" : sum % 1 === 0 ? String(sum) : String(sum);
});

const totalArea = computed(() => {
  const sum = form.value.entries.reduce((acc, e) => {
    const v = parseFloat(e.area);
    return acc + (isNaN(v) ? 0 : v);
  }, 0);
  return sum === 0 ? "" : sum % 1 === 0 ? String(sum) : String(sum);
});
const error = ref("");
const successMsg = ref("");
const saving = ref(false);
const sending = ref(false);
const savedOrNavigated = ref(false);
const showSaveModal = ref(false);
const showSendModal = ref(false);

function isFormDirty() {
  return form.value.entries.some(
    (e) => e.hours || e.work_code || e.area || e.objects || e.description,
  );
}

onBeforeRouteLeave(async () => {
  if (isNew.value && isFormDirty() && !savedOrNavigated.value) {
    savedOrNavigated.value = true;
    const payload = {
      week_number: form.value.week_number,
      year: form.value.year,
      status: "draft",
      project_id: form.value.project_id,
      entries: form.value.entries,
    };
    try {
      await store.createReport(payload);
    } catch {
      // silently ignore – don't block navigation
    }
  }
});

onMounted(async () => {
  await Promise.all([store.fetchWorkCodes(), projectsStore.fetchProjects()]);
  // Pre-select project from query param (e.g. from ProjectView)
  if (route.query.project_id) {
    form.value.project_id = parseInt(route.query.project_id);
  }
  if (!isNew.value && reportId.value) {
    await store.fetchReport(reportId.value);
    const r = store.currentReport;
    form.value.week_number = r.week_number;
    form.value.year = r.year;
    form.value.project_id = r.project_id ?? null;
    form.value.entries = DAYS.flatMap((day) => {
      const existing = r.entries.filter((e) => e.day === day);
      return existing.length > 0
        ? existing.map((e) => ({
            day,
            hours: e.hours,
            area: e.area,
            objects: e.objects,
            description: e.description,
            work_code: e.work_code,
          }))
        : [
            {
              day,
              hours: null,
              area: null,
              objects: null,
              description: null,
              work_code: null,
            },
          ];
    });
  }
});

async function handleSave() {
  showSaveModal.value = false;
  error.value = "";
  successMsg.value = "";
  saving.value = true;
  try {
    const payload = {
      week_number: form.value.week_number,
      year: form.value.year,
      project_id: form.value.project_id,
      entries: form.value.entries,
    };
    if (isNew.value) {
      const created = await store.createReport({ ...payload, status: "saved" });
      savedOrNavigated.value = true;
      successMsg.value = "Raportti tallennettu!";
      router.replace(`/reports/${created.id}/edit`);
    } else {
      await store.updateReport(reportId.value, payload);
      successMsg.value = "Raportti päivitetty!";
    }
  } catch (e) {
    error.value = e.response?.data?.detail || "Raportin tallennus epäonnistui.";
  } finally {
    saving.value = false;
  }
}

function handleDownloadPdf() {
  store
    .downloadPdf(reportId.value, form.value.week_number, form.value.year)
    .catch(() => {
      error.value = "PDF-tiedoston lataaminen epaonnistui.";
    });
}

async function handleSend() {
  showSendModal.value = false;
  error.value = "";
  successMsg.value = "";
  sending.value = true;
  try {
    await store.sendReport(reportId.value);
    successMsg.value = "✅ Raportti lähetetty onnistuneesti!";
  } catch (e) {
    error.value = e.response?.data?.detail || "Raportin lähetys epäonnistui.";
  } finally {
    sending.value = false;
  }
}
</script>
