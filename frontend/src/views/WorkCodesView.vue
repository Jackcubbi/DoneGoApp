<template>
  <div class="workcodes-page">
    <div class="workcodes-page__header">
      <h1>Work Codes</h1>
      <p class="text-muted">
        System codes are read-only. Add your own custom codes below.
      </p>
    </div>

    <div class="workcodes-list">
      <div v-for="wc in workCodes" :key="wc.id" class="workcode-item">
        <template v-if="editingId === wc.id">
          <input
            v-model.number="editForm.code"
            type="number"
            class="input-sm"
            style="width: 70px"
          />
          <input
            v-model="editForm.description"
            type="text"
            class="input-sm"
            style="flex: 1"
          />
          <button
            class="btn btn--sm btn--primary"
            @click="showSaveEditModal = true"
          >
            <CheckIcon :size="13" /> Save
          </button>
          <button class="btn btn--sm btn--outline" @click="editingId = null">
            <XIcon :size="13" /> Cancel
          </button>
        </template>

        <template v-else>
          <span class="workcode-code">{{ wc.code }}</span>
          <span class="workcode-desc">{{ wc.description }}</span>
          <span v-if="wc.user_id === null" class="badge badge--system"
            >system</span
          >
          <div v-else class="workcode-actions">
            <button class="btn btn--sm btn--outline" @click="startEdit(wc)">
              <PencilIcon :size="13" /> Edit
            </button>
            <button
              class="btn btn--sm btn--danger"
              @click="confirmRemove(wc.id)"
            >
              <Trash2Icon :size="13" /> Delete
            </button>
          </div>
        </template>
      </div>
    </div>

    <div class="workcode-add">
      <h2>Add Custom Work Code</h2>
      <div class="workcode-add__row">
        <input
          v-model.number="newForm.code"
          type="number"
          class="input-sm"
          placeholder="Code"
          style="width: 80px"
        />
        <input
          v-model="newForm.description"
          type="text"
          class="input-sm"
          placeholder="Description (e.g. Maalaus)"
          style="flex: 1"
        />
        <button class="btn btn--primary" @click="showAddModal = true">
          <PlusIcon :size="15" /> Add
        </button>
      </div>
      <p v-if="addError" class="error-msg" style="margin-top: 8px">
        {{ addError }}
      </p>
    </div>
  </div>

  <ConfirmModal
    v-model="showAddModal"
    title="Lisää työvaihekoodi?"
    :message="`Lisätään koodi ${newForm.code} – ${newForm.description}`"
    confirm-label="Lisää"
    icon="add"
    variant="info"
    @confirm="addCode"
    @cancel="showAddModal = false"
  />

  <ConfirmModal
    v-model="showSaveEditModal"
    title="Tallenna muutokset?"
    message="Haluatko tallentaa tämän työvaihekodin muutokset?"
    confirm-label="Tallenna"
    icon="save"
    variant="info"
    @confirm="saveEdit(editingId)"
    @cancel="showSaveEditModal = false"
  />

  <ConfirmModal
    v-model="showDeleteModal"
    title="Poista työvaihekoodi?"
    message="Tätä toimintoa ei voi kumota."
    confirm-label="Poista"
    icon="trash"
    variant="danger"
    @confirm="removeCode"
    @cancel="showDeleteModal = false"
  />
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import {
  PencilIcon,
  Trash2Icon,
  CheckIcon,
  XIcon,
  PlusIcon,
} from "lucide-vue-next";
import { useReportsStore } from "../stores/reports";
import ConfirmModal from "../components/ConfirmModal.vue";

const store = useReportsStore();
const workCodes = computed(() => store.workCodes);

const editingId = ref(null);
const editForm = ref({ code: 0, description: "" });
const newForm = ref({ code: "", description: "" });
const addError = ref("");

const showAddModal = ref(false);
const showSaveEditModal = ref(false);
const showDeleteModal = ref(false);
const pendingDeleteId = ref(null);

onMounted(() => store.fetchWorkCodes());

function startEdit(wc) {
  editingId.value = wc.id;
  editForm.value = { code: wc.code, description: wc.description };
}

async function saveEdit(id) {
  showSaveEditModal.value = false;
  await store.updateWorkCode(id, editForm.value);
  editingId.value = null;
}

function confirmRemove(id) {
  pendingDeleteId.value = id;
  showDeleteModal.value = true;
}

async function removeCode() {
  showDeleteModal.value = false;
  await store.deleteWorkCode(pendingDeleteId.value);
  pendingDeleteId.value = null;
}

async function addCode() {
  showAddModal.value = false;
  addError.value = "";
  if (!newForm.value.code || !newForm.value.description.trim()) {
    addError.value = "Both code number and description are required.";
    return;
  }
  try {
    await store.createWorkCode({
      code: newForm.value.code,
      description: newForm.value.description,
    });
    newForm.value = { code: "", description: "" };
  } catch (e) {
    addError.value = e.response?.data?.detail || "Failed to add work code.";
  }
}
</script>
