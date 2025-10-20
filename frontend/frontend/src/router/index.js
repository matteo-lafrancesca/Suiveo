import { createRouter, createWebHistory } from "vue-router";
import LoginView from "@/views/LoginView.vue";
import Dashboard from "@/views/Dashboard.vue";
import TableauSuivi from "@/views/TableauSuivi.vue";

// 🔍 Fonction utilitaire : vérifie si l'utilisateur est connecté
function isAuthenticated() {
  const token = localStorage.getItem("access");
  return !!token; // true si token existe, false sinon
}

const routes = [
  {
    path: "/",
    redirect: () => {
      // Si connecté → dashboard, sinon → login
      return isAuthenticated() ? "/dashboard" : "/login";
    },
  },
  {
    path: "/login",
    name: "Login",
    component: LoginView,
    // Si déjà connecté → empêche d'aller sur /login
    beforeEnter: (to, from, next) => {
      if (isAuthenticated()) next("/dashboard");
      else next();
    },
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
    // Si pas connecté → empêche d'aller sur /dashboard
    beforeEnter: (to, from, next) => {
      if (!isAuthenticated()) next("/login");
      else next();
    },
  },
  {
    path : "/tableau-suivi",
    name : "Tableau Suivi",
    component: TableauSuivi,
    beforeEnter: (to, from, next) => {
      if (!isAuthenticated()) next("/login");
      else next();
    },
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
