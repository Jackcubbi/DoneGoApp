import { defineStore } from "pinia";
import api from "../api";

export const useReportsStore = defineStore("reports", {
  state: () => ({
    reports: [],
    currentReport: null,
    workCodes: [],
  }),

  actions: {
    async fetchReports() {
      const { data } = await api.get("/reports");
      this.reports = data;
    },

    async fetchReport(id) {
      const { data } = await api.get(`/reports/${id}`);
      this.currentReport = data;
    },

    async createReport(payload) {
      const { data } = await api.post("/reports", payload);
      return data;
    },

    async updateReport(id, payload) {
      const { data } = await api.put(`/reports/${id}`, payload);
      this.currentReport = data;
      return data;
    },

    async sendReport(id) {
      const { data } = await api.post(`/reports/${id}/send`);
      if (this.currentReport?.id === id) {
        this.currentReport = { ...this.currentReport, status: "sent" };
      }
      const idx = this.reports.findIndex((r) => r.id === id);
      if (idx !== -1)
        this.reports[idx] = { ...this.reports[idx], status: "sent" };
      return data;
    },

    async fetchWorkCodes() {
      const { data } = await api.get("/workcodes");
      this.workCodes = data;
    },

    async createWorkCode(payload) {
      const { data } = await api.post("/workcodes", payload);
      this.workCodes.push(data);
    },

    async updateWorkCode(id, payload) {
      const { data } = await api.put(`/workcodes/${id}`, payload);
      const idx = this.workCodes.findIndex((w) => w.id === id);
      if (idx !== -1) this.workCodes[idx] = data;
    },

    async deleteWorkCode(id) {
      await api.delete(`/workcodes/${id}`);
      this.workCodes = this.workCodes.filter((w) => w.id !== id);
    },

    async deleteReport(id) {
      await api.delete(`/reports/${id}`);
      this.reports = this.reports.filter((r) => r.id !== id);
    },

    async downloadPdf(id, weekNumber, year) {
      const token = localStorage.getItem("token");
      const res = await fetch(`/api/reports/${id}/pdf`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const err = await res.text();
        throw new Error(err || "PDF download failed");
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `report_week${weekNumber}_${year}.pdf`;
      link.click();
      URL.revokeObjectURL(url);
    },
  },
});
