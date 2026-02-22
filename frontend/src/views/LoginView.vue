<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-card__logo">
        <img src="/logo.svg" alt="DoneGo" class="auth-logo" />
      </div>
      <p class="auth-card__subtitle">Kirjaudu sisään tilillesi</p>

      <form class="auth-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Sähköposti</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            autocomplete="email"
            placeholder="you@example.com"
          />
        </div>

        <div class="form-group">
          <label for="password">Salasana</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            autocomplete="current-password"
            placeholder="••••••••"
          />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button
          type="submit"
          class="btn btn--primary btn--full"
          :disabled="loading"
        >
          {{ loading ? "Kirjaudutaan sisään…" : "Kirjaudu sisään" }}
        </button>
      </form>

      <p class="auth-card__footer">
        Ei tiliä?
        <RouterLink to="/register">Luo tili</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";

const auth = useAuthStore();
const router = useRouter();

const form = ref({ email: "", password: "" });
const error = ref("");
const loading = ref(false);

async function handleLogin() {
  error.value = "";
  loading.value = true;
  try {
    await auth.login(form.value.email, form.value.password);
    router.push("/dashboard");
  } catch (e) {
    error.value =
      e.response?.data?.detail ||
      "Kirjautuminen epäonnistui. Tarkista tunnistetietosi.";
  } finally {
    loading.value = false;
  }
}
</script>
