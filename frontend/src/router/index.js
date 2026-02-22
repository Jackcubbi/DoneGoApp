import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

const routes = [
  { path: "/", redirect: "/dashboard" },
  {
    path: "/login",
    component: () => import("../views/LoginView.vue"),
    meta: { guest: true },
  },
  {
    path: "/register",
    component: () => import("../views/RegisterView.vue"),
    meta: { guest: true },
  },
  {
    path: "/dashboard",
    component: () => import("../views/DashboardView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/reports/:id/view",
    component: () => import("../views/ReportViewView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/reports/new",
    component: () => import("../views/ReportEditView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/reports/:id/edit",
    component: () => import("../views/ReportEditView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/workcodes",
    component: () => import("../views/WorkCodesView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/projects/new",
    component: () => import("../views/ProjectNewView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/projects/:id/edit",
    component: () => import("../views/ProjectEditView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/projects/:id",
    component: () => import("../views/ProjectView.vue"),
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore();
  if (to.meta.requiresAuth && !auth.isLoggedIn) return next("/login");
  if (to.meta.guest && auth.isLoggedIn) return next("/dashboard");
  next();
});

export default router;
