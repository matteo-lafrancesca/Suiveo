import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";

// --- VUES ---
import LoginView from "@/views/LoginView.vue";
import Dashboard from "@/views/Dashboard.vue";
import TableauSuivi from "@/views/TableauSuivi.vue";
import Binome from "@/views/Binome.vue";
import Planning from "@/views/Planning.vue";
import ListeBinome from "@/views/ListeBinome.vue";
import Gestion from "@/views/Gestion.vue";
import CreateBinome from "@/views/CreateBinome.vue";
import CreateSupervisor from "@/views/CreateSupervisor.vue";
import ActivateAccount from "@/views/ActivateAccount.vue";
import Profile from "@/views/Profile.vue";

const routes = [
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/login",
    name: "Login",
    component: LoginView,
    meta: { guest: true }, // Accessible seulement si non connecté
  },
  {
    path: "/activate-account",
    name: "ActivateAccount",
    component: ActivateAccount,
    meta: { public: true },
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: "/tableau-suivi",
    name: "TableauSuivi",
    component: TableauSuivi,
    meta: { requiresAuth: true },
  },
  {
    path: "/binome/:id",
    name: "Binome",
    component: Binome,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: "/planning",
    name: "Planning",
    component: Planning,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: "/liste-binomes",
    name: "Liste Binomes",
    component: ListeBinome,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: "/creation-gestion",
    name: "Création Gestion",
    component: Gestion,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: "/creation-binome",
    name: "Création Binome",
    component: CreateBinome,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: "/create-supervisor",
    name: "CreateSupervisor",
    component: CreateSupervisor,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: "/profil",
    name: "Profile",
    component: Profile,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// --- GLOBAL GUARDS ---
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;
  const isAdmin = authStore.isAdmin;

  // 1. Redirection si la route nécessite une auth et utilisateur non connecté
  if (to.meta.requiresAuth && !isAuthenticated) {
    next("/login");
    return;
  }

  // 2. Redirection page Login si déjà connecté
  if (to.meta.guest && isAuthenticated) {
    next("/dashboard");
    return;
  }

  // 3. Protection Admin
  if (to.meta.requiresAdmin && !isAdmin) {
    next("/dashboard"); // ou page 403
    return;
  }

  next();
});

export default router;
