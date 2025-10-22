import { createRouter, createWebHistory } from "vue-router";
import LoginView from "@/views/LoginView.vue";
import Dashboard from "@/views/Dashboard.vue";
import TableauSuivi from "@/views/TableauSuivi.vue";
import Binome from "@/views/Binome.vue"; // 👈 nouvelle vue importée
import Planning from "@/views/Planning.vue";
import ListeBinome from "@/views/ListeBinome.vue";
import Gestion from "@/views/Gestion.vue";
import CreateBinome from "@/views/CreateBinome.vue";

// 🔍 Vérifie si l'utilisateur est connecté
function isAuthenticated() {
  const token = localStorage.getItem("access");
  return !!token;
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
    beforeEnter: (to, from, next) => {
      if (isAuthenticated()) next("/dashboard");
      else next();
    },
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
    beforeEnter: (to, from, next) => {
      if (!isAuthenticated()) next("/login");
      else next();
    },
  },
  {
    path: "/tableau-suivi",
    name: "TableauSuivi",
    component: TableauSuivi,
    beforeEnter: (to, from, next) => {
      if (!isAuthenticated()) next("/login");
      else next();
    },
  },
  {
    path: "/binome/:id", // 👈 route dynamique
    name: "Binome",
    component: Binome,
    props: true, // permet de passer automatiquement l'id à la vue
    beforeEnter: (to, from, next) => {
      if (!isAuthenticated()) next("/login");
      else next();
    },
  },
  {
    path: "/planning",
    name: "Planning",
    component: Planning,
    props: true, // permet de passer automatiquement l'id à la vue
    beforeEnter: (to, from, next) => {
      if (!isAuthenticated()) next("/login");
      else next();
    },
  },
  {
    path: "/liste-binomes",
    name: "Liste Binomes",
    component: ListeBinome,
    props: true, // permet de passer automatiquement l'id à la vue
    beforeEnter: (to, from, next) => {
      if (!isAuthenticated()) next("/login");
      else next();
    },
  },
    {
    path: "/creation-gestion",
    name: "Création Gestion",
    component: Gestion,
    props: true, // permet de passer automatiquement l'id à la vue
    beforeEnter: (to, from, next) => {
      if (!isAuthenticated()) next("/login");
      else next();
    },
  },
  {
    path: "/creation-binome",
    name: "Création Binome",
    component: CreateBinome,
    props: true, // permet de passer automatiquement l'id à la vue
    beforeEnter: (to, from, next) => {
      if (!isAuthenticated()) next("/login");
      else next();
    },
  },
  
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
