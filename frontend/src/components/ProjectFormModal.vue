<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="modal-overlay"
        @mousedown.self="$emit('cancel')"
      >
        <div class="modal-box modal-box--form" role="dialog" aria-modal="true">
          <h3 class="modal-title">
            {{ isEdit ? "Muokkaa projektia" : "Uusi projekti" }}
          </h3>

          <div class="project-form">
            <div class="project-form__field">
              <label>Projekti-ID</label>
              <input
                v-model="draft.project_code"
                type="text"
                placeholder="PRJ-001"
              />
            </div>
            <div class="project-form__field project-form__field--full">
              <label>Projektin nimi <span class="required">*</span></label>
              <input
                v-model="draft.name"
                type="text"
                placeholder="Projektin nimi"
                :class="{ 'input--error': nameError }"
              />
            </div>
            <div class="project-form__field project-form__field--full">
              <label>Osoite</label>
              <input
                v-model="draft.address"
                type="text"
                placeholder="Katuosoite, kaupunki"
              />
            </div>
            <div class="project-form__field">
              <label>Pääurakoitsija</label>
              <input
                v-model="draft.general_company"
                type="text"
                placeholder="Yleisurakoitsijan nimi"
              />
            </div>
            <div class="project-form__field">
              <label>Työnantaja</label>
              <input
                v-model="draft.employer"
                type="text"
                placeholder="Oma työnantaja"
              />
            </div>
          </div>

          <p v-if="nameError" class="field-error">
            Projektin nimi on pakollinen.
          </p>

          <div class="modal-actions">
            <button class="btn btn--outline" @click="$emit('cancel')">
              Peruuta
            </button>
            <button
              class="btn btn--primary"
              :disabled="loading"
              @click="handleSubmit"
            >
              <LoaderIcon v-if="loading" :size="14" class="spin" />
              {{
                loading ? "Tallennetaan…" : isEdit ? "Tallenna" : "Luo projekti"
              }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { LoaderIcon } from "lucide-vue-next";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  initial: { type: Object, default: null },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue", "confirm", "cancel"]);

const isEdit = computed(() => !!props.initial?.id);
const nameError = ref(false);

const empty = () => ({
  project_code: "",
  name: "",
  address: "",
  general_company: "",
  employer: "",
});

const draft = ref(empty());

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      nameError.value = false;
      draft.value = props.initial ? { ...props.initial } : empty();
    }
  },
);

function handleSubmit() {
  if (!draft.value.name?.trim()) {
    nameError.value = true;
    return;
  }
  nameError.value = false;
  emit("confirm", { ...draft.value });
}
</script>
