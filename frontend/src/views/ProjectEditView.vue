<template>
  <div class="project-edit">
    <div class="project-edit__header">
      <RouterLink :to="`/projects/${projectId}`" class="back-link">
        <ArrowLeftIcon />
        <p>Projekti</p>
      </RouterLink>
      <h1>Muokkaa projektia</h1>
    </div>

    <div v-if="notFound" class="empty-state">
      <p>Projektia ei löydy.</p>
      <RouterLink
        to="/dashboard"
        class="btn btn--outline"
        style="margin-top: 16px"
      >
        Palaa työpöydälle
      </RouterLink>
    </div>

    <div v-else class="project-edit__card">
      <div class="form-row">
        <div class="form-group">
          <label>Projekti-ID</label>
          <input
            v-model="form.project_code"
            type="text"
            placeholder="PRJ-001"
          />
        </div>
        <div class="form-group">
          <label>Projektin nimi <span class="required">*</span></label>
          <input
            v-model="form.name"
            type="text"
            placeholder="Kirjoita projektin nimi"
            :class="{ 'input--error': nameError }"
            @input="nameError = false"
          />
          <span v-if="nameError" class="field-error">Nimi on pakollinen.</span>
        </div>
      </div>

      <div class="form-group">
        <label>Osoite</label>
        <input
          v-model="form.address"
          type="text"
          placeholder="Katuosoite, kaupunki"
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Pääurakoitsija</label>
          <input
            v-model="form.general_company"
            type="text"
            placeholder="Yleisurakoitsijan nimi"
          />
        </div>
        <div class="form-group">
          <label>Työnantaja</label>
          <input
            v-model="form.employer"
            type="text"
            placeholder="Oma työnantaja"
          />
        </div>
      </div>

      <p v-if="error" class="error-msg">{{ error }}</p>

      <div class="project-edit__actions">
        <RouterLink :to="`/projects/${projectId}`" class="btn btn--outline">
          Peruuta
        </RouterLink>
        <button class="btn btn--primary" :disabled="saving" @click="handleSave">
          <LoaderIcon v-if="saving" :size="14" class="spin" />
          {{ saving ? "Tallennetaan…" : "Tallenna muutokset" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ArrowLeftIcon, LoaderIcon } from "lucide-vue-next";
import { useRoute, useRouter } from "vue-router";
import { useProjectsStore } from "../stores/projects";

const route = useRoute();
const router = useRouter();
const store = useProjectsStore();

const projectId = computed(() => parseInt(route.params.id));

const saving = ref(false);
const nameError = ref(false);
const error = ref("");
const notFound = ref(false);

const form = ref({
  project_code: "",
  name: "",
  address: "",
  general_company: "",
  employer: "",
});

async function handleSave() {
  if (!form.value.name?.trim()) {
    nameError.value = true;
    return;
  }
  saving.value = true;
  error.value = "";
  try {
    await store.updateProject(projectId.value, form.value);
    router.replace(`/projects/${projectId.value}`);
  } catch (e) {
    error.value =
      e.response?.data?.detail || "Projektin tallentaminen epäonnistui.";
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  await store.fetchProjects();
  const project = store.projects.find((p) => p.id === projectId.value);
  if (!project) {
    notFound.value = true;
    return;
  }
  form.value = {
    project_code: project.project_code ?? "",
    name: project.name ?? "",
    address: project.address ?? "",
    general_company: project.general_company ?? "",
    employer: project.employer ?? "",
  };
});
</script>
