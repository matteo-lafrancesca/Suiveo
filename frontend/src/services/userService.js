import api from "./api";

export async function createSupervisor(userData) {
  const data = { ...userData, role: "Supervisor" };
  return api.post("/users/create/", data);
}

export async function inviteSupervisor(email) {
  return api.post("/users/invite/", { email });
}

export async function activateAccount(data) {
  return api.post("/users/activate/", data);
}

export async function checkActivationToken(uid, token) {
  return api.get(`/users/activate/?uid=${uid}&token=${token}`);
}
