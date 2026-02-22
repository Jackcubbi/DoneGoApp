<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="modal-overlay"
        @mousedown.self="$emit('cancel')"
      >
        <div class="modal-box" role="dialog" aria-modal="true">
          <div v-if="icon" class="modal-icon" :class="`modal-icon--${variant}`">
            <component :is="iconComponent" :size="28" />
          </div>
          <h3 class="modal-title">{{ title }}</h3>
          <p v-if="message" class="modal-message">{{ message }}</p>
          <div class="modal-actions">
            <button class="btn btn--outline" @click="$emit('cancel')">
              {{ cancelLabel }}
            </button>
            <button
              class="btn"
              :class="confirmClass"
              :disabled="loading"
              @click="$emit('confirm')"
            >
              <component
                v-if="loading"
                :is="LoaderIcon"
                :size="14"
                class="spin"
              />
              {{ loading ? "Odota…" : confirmLabel }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from "vue";
import {
  AlertTriangleIcon,
  Trash2Icon,
  SaveIcon,
  SendIcon,
  LogOutIcon,
  PlusIcon,
  LoaderIcon,
  CheckCircleIcon,
} from "lucide-vue-next";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: "Vahvista toiminto" },
  message: { type: String, default: "" },
  confirmLabel: { type: String, default: "Vahvista" },
  cancelLabel: { type: String, default: "Peruuta" },
  variant: { type: String, default: "danger" }, // danger | warning | info | success
  icon: { type: String, default: "alert" }, // alert | trash | save | send | logout | add | check
  loading: { type: Boolean, default: false },
});

defineEmits(["update:modelValue", "confirm", "cancel"]);

const confirmClass = computed(() => ({
  "btn--danger": props.variant === "danger",
  "btn--primary": props.variant === "info" || props.variant === "success",
  "btn--warning": props.variant === "warning",
}));

const iconMap = {
  alert: AlertTriangleIcon,
  trash: Trash2Icon,
  save: SaveIcon,
  send: SendIcon,
  logout: LogOutIcon,
  add: PlusIcon,
  check: CheckCircleIcon,
};

const iconComponent = computed(() => iconMap[props.icon] ?? AlertTriangleIcon);
</script>

<style lang="scss" scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-box {
  background: #fff;
  border-radius: 12px;
  padding: 32px 28px 24px;
  width: min(420px, 90vw);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.modal-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  margin: 0 auto 16px;

  &--danger {
    background: #ffeaea;
    color: #e74c3c;
  }
  &--warning {
    background: #fff8e1;
    color: #f39c12;
  }
  &--info {
    background: #eaf4fb;
    color: #2980b9;
  }
  &--success {
    background: #eafaf1;
    color: #27ae60;
  }
}

.modal-title {
  font-size: 1.05rem;
  font-weight: 700;
  margin: 0 0 8px;
  color: #2d3436;
}

.modal-message {
  font-size: 0.875rem;
  color: #636e72;
  margin: 0 0 24px;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: center;

  .btn {
    min-width: 110px;
  }
}

.spin {
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

// Transition
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.18s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-active .modal-box,
.modal-leave-active .modal-box {
  transition: transform 0.18s ease;
}
.modal-enter-from .modal-box {
  transform: scale(0.92);
}
.modal-leave-to .modal-box {
  transform: scale(0.92);
}
</style>
