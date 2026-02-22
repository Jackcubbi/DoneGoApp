import { defineStore } from "pinia";
import api from "../api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    token: localStorage.getItem("token") || null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    async login(email, password) {
      const { data } = await api.post("/login", { email, password });
      this.token = data.access_token;
      localStorage.setItem("token", data.access_token);
      await this.fetchMe();
    },

    async register(payload) {
      await api.post("/register", payload);
    },

    async fetchMe() {
      const { data } = await api.get("/me");
      this.user = data;
    },

    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem("token");
    },
  },
});
