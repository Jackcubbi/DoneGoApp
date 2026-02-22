<template>
  <div id="app">
    <NavBar v-if="auth.isLoggedIn" />
    <main :class="['main-content', { 'main-content--full': !auth.isLoggedIn }]">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { useAuthStore } from "./stores/auth";
import NavBar from "./components/NavBar.vue";

const auth = useAuthStore();

onMounted(async () => {
  if (auth.isLoggedIn && !auth.user) {
    try {
      await auth.fetchMe();
    } catch {
      auth.logout();
    }
  }
});
</script>
