<template>
  <nav class="navbar">
    <div class="navbar__brand">
      <RouterLink to="/dashboard">
        <img src="/logo.svg" alt="DoneGo" class="navbar-logo" />
      </RouterLink>
    </div>

    <div class="navbar__links" :class="{ 'navbar__links--open': menuOpen }">
      <RouterLink to="/dashboard" @click="menuOpen = false">
        <LayoutDashboardIcon :size="18" /> Työpöytä
      </RouterLink>
      <RouterLink to="/projects/new" @click="menuOpen = false">
        <FilePlusIcon :size="18" /> Uusi projekti
      </RouterLink>
      <RouterLink to="/workcodes" @click="menuOpen = false">
        <ListIcon :size="18" /> Työkoodit
      </RouterLink>
      <RouterLink to="/stats" @click="menuOpen = false">
        <BarChart2Icon :size="18" /> Statistiikka
      </RouterLink>
      <!-- Mobile-only user info + logout inside the drawer -->
      <div class="navbar__mobile-user">
        <span v-if="auth.user" class="navbar__name">
          <UserIcon :size="16" />
          {{ auth.user.name }} {{ auth.user.surname }}
        </span>
        <button
          class="btn btn--sm btn--outline-light"
          @click="
            showLogout = true;
            menuOpen = false;
          "
        >
          <LogOutIcon :size="16" /> Kirjaudu ulos
        </button>
      </div>
    </div>

    <div class="navbar__user">
      <span v-if="auth.user" class="navbar__name">
        <UserIcon :size="18" />
        {{ auth.user.name }} {{ auth.user.surname }}
      </span>
      <button class="btn btn--sm btn--outline-light" @click="showLogout = true">
        <LogOutIcon :size="18" /> Kirjaudu ulos
      </button>
    </div>

    <!-- Hamburger button (mobile only) -->
    <button
      class="navbar__hamburger"
      :class="{ 'navbar__hamburger--open': menuOpen }"
      :aria-expanded="menuOpen"
      aria-label="Toggle menu"
      @click="menuOpen = !menuOpen"
    >
      <span /><span /><span />
    </button>
  </nav>

  <!-- Backdrop -->
  <div v-if="menuOpen" class="navbar__backdrop" @click="menuOpen = false" />

  <ConfirmModal
    v-model="showLogout"
    title="Kirjaudu ulos?"
    message="Haluatko varmasti kirjautua ulos?"
    confirm-label="Kirjaudu ulos"
    icon="logout"
    variant="warning"
    @confirm="handleLogout"
    @cancel="showLogout = false"
  />
</template>

<script setup>
import {
  LayoutDashboardIcon,
  FilePlusIcon,
  ListIcon,
  BarChart2Icon,
  UserIcon,
  LogOutIcon,
} from "lucide-vue-next";
import { ref } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import ConfirmModal from "./ConfirmModal.vue";

const auth = useAuthStore();
const router = useRouter();
const showLogout = ref(false);
const menuOpen = ref(false);

function handleLogout() {
  showLogout.value = false;
  auth.logout();
  router.push("/login");
}
</script>
