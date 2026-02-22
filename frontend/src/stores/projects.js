import { defineStore } from "pinia";
import api from "../api";

export const useProjectsStore = defineStore("projects", {
  state: () => ({
    projects: [],
  }),

  actions: {
    async fetchProjects() {
      const { data } = await api.get("/projects");
      this.projects = data;
    },

    async createProject(payload) {
      const { data } = await api.post("/projects", payload);
      this.projects.unshift(data);
      return data;
    },

    async updateProject(id, payload) {
      const { data } = await api.put(`/projects/${id}`, payload);
      const idx = this.projects.findIndex((p) => p.id === id);
      if (idx !== -1) this.projects[idx] = data;
      return data;
    },

    async deleteProject(id) {
      await api.delete(`/projects/${id}`);
      this.projects = this.projects.filter((p) => p.id !== id);
    },
  },
});
