import api from "./api";

export async function login(email, password) {
  const response = await api.post("/login/", { email, password });
  const { access, refresh, user } = response.data;

  // On stocke les tokens pour les prochaines requêtes
  localStorage.setItem("access", access);
  localStorage.setItem("refresh", refresh);
  localStorage.setItem("user", JSON.stringify(user));

  return user;
}

export async function refreshToken() {
  const refresh = localStorage.getItem("refresh");
  if (!refresh) return null;

  const response = await api.post("/token/refresh/", { refresh });
  localStorage.setItem("access", response.data.access);
  return response.data.access;
}

export function logout() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  localStorage.removeItem("user");
}
