<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-card__logo">
        <img src="/logo.svg" alt="DoneGo" class="auth-logo" />
      </div>
      <p class="auth-card__subtitle">Create your account</p>

      <form class="auth-form" @submit.prevent="handleRegister">
        <div class="form-row">
          <div class="form-group">
            <label for="name">First Name</label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              placeholder="John"
            />
          </div>
          <div class="form-group">
            <label for="surname">Last Name</label>
            <input
              id="surname"
              v-model="form.surname"
              type="text"
              required
              placeholder="Doe"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="email">Email</label>
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
          <label for="phone"
            >Phone <span class="optional">(optional)</span></label
          >
          <input
            id="phone"
            v-model="form.phone"
            type="tel"
            placeholder="+358 40 123 4567"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            minlength="6"
            autocomplete="new-password"
            placeholder="At least 6 characters"
          />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button
          type="submit"
          class="btn btn--primary btn--full"
          :disabled="loading"
        >
          {{ loading ? "Creating…" : "Create Account" }}
        </button>
      </form>

      <p class="auth-card__footer">
        Already have an account?
        <RouterLink to="/login">Sign In</RouterLink>
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

const form = ref({ name: "", surname: "", email: "", phone: "", password: "" });
const error = ref("");
const loading = ref(false);

async function handleRegister() {
  error.value = "";
  loading.value = true;
  try {
    await auth.register(form.value);
    await auth.login(form.value.email, form.value.password);
    router.push("/dashboard");
  } catch (e) {
    error.value = e.response?.data?.detail || "Registration failed. Try again.";
  } finally {
    loading.value = false;
  }
}
</script>
