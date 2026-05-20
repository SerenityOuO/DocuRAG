import { createRouter, createWebHistory } from "vue-router";

import Dashboard from "../pages/Dashboard.vue";
import Documents from "../pages/Documents.vue";
import Login from "../pages/Login.vue";
import Projects from "../pages/Projects.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "dashboard", component: Dashboard },
    { path: "/login", name: "login", component: Login },
    { path: "/projects", name: "projects", component: Projects },
    { path: "/documents", name: "documents", component: Documents },
  ],
});
