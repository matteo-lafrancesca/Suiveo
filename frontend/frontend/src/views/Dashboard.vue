<template>
  <v-container class="d-flex flex-column align-center justify-center" style="height: 100vh; margin-top: -10vh;">
    <v-card elevation="6" class="pa-8 text-center rounded-xl" width="500">
      <h2 class="text-h5 font-weight-bold mb-4 text-primary">
        Tableau de bord
      </h2>

      <div v-if="user">
        <p class="text-body-1 mb-2">
          👋 Bonjour <strong>{{ user.first_name }} {{ user.last_name }}</strong> !
        </p>
        <p class="text-grey">
          Rôle : <strong>{{ user.role }}</strong>
        </p>
      </div>

      <v-divider class="my-6"></v-divider>

      <v-btn color="error" rounded="lg" block @click="logoutUser">
        Se déconnecter
      </v-btn>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const user = ref(null);

// --------------------
// Charger les infos utilisateur
// --------------------
onMounted(async () => {
  const token = localStorage.getItem("access");
  if (!token) {
    window.location.href = "/login"; // pas de token → redirection
    return;
  }

  try {
    const response = await axios.get("http://127.0.0.1:8000/api/me/", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    user.value = response.data;
  } catch (error) {
    console.error("Erreur :", error);
    localStorage.clear();
    window.location.href = "/login";
  }
});

// --------------------
// Logout
// --------------------
function logoutUser() {
  localStorage.clear();
  window.location.href = "/login";
}
</script>
