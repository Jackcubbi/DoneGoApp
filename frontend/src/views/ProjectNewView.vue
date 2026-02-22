<template>
  <div class="project-edit">
    <div class="project-edit__header">
      <RouterLink to="/dashboard" class="back-link">
        <ArrowLeftIcon />
        <p>Työpöytä</p>
      </RouterLink>
      <h1>Uusi projekti</h1>
    </div>

    <div class="project-edit__card">
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
        <RouterLink to="/dashboard" class="btn btn--outline">
          Peruuta
        </RouterLink>
        <button class="btn btn--primary" :disabled="saving" @click="handleSave">
          <LoaderIcon v-if="saving" :size="14" class="spin" />
          {{ saving ? "Tallennetaan…" : "Luo projekti" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { ArrowLeftIcon, LoaderIcon } from "lucide-vue-next";
import { useRouter } from "vue-router";
import { useProjectsStore } from "../stores/projects";

const router = useRouter();
const store = useProjectsStore();

const saving = ref(false);
const nameError = ref(false);
const error = ref("");

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
    const project = await store.createProject(form.value);
    router.replace(`/projects/${project.id}`);
  } catch (e) {
    error.value = e.response?.data?.detail || "Projektin luominen epäonnistui.";
  } finally {
    saving.value = false;
  }
}
</script>
