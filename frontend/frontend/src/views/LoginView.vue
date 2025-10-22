<template>
  <v-sheet
    class="d-flex align-center justify-center login-container"
    color="background"
  >
    <v-card
      elevation="8"
      max-width="480"
      width="90%"
      class="pa-10 rounded-xl text-center"
    >
      <h2 class="text-h5 font-weight-bold mb-6 text-primary">
        Connexion
      </h2>

      <v-form @submit.prevent="handleLogin">
        <v-text-field
          v-model="email"
          label="Adresse e-mail"
          prepend-inner-icon="mdi-email-outline"
          variant="outlined"
          color="primary"
          class="mb-4"
        />

        <v-text-field
          v-model="password"
          label="Mot de passe"
          prepend-inner-icon="mdi-lock-outline"
          type="password"
          variant="outlined"
          color="primary"
          class="mb-6"
        />

        <v-btn
          type="submit"
          color="primary"
          block
          rounded="lg"
          size="large"
          class="font-weight-bold"
          :loading="loading"
        >
          Se connecter
        </v-btn>

        <p v-if="error" class="text-red mt-4">{{ error }}</p>
      </v-form>
    </v-card>
  </v-sheet>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";

const router = useRouter();

const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);

const handleLogin = async () => {
  error.value = "";
  loading.value = true;

  try {
    const response = await axios.post("http://127.0.0.1:8000/api/login/", {
      email: email.value,
      password: password.value,
    });

    const { access, refresh, user } = response.data;
    localStorage.setItem("access", access);
    localStorage.setItem("refresh", refresh);
    localStorage.setItem("user", JSON.stringify(user));

    router.push("/");
  } catch (err) {
    console.error(err);
    error.value =
      err.response?.data?.error || "Email ou mot de passe incorrect.";
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  min-height: calc(100vh - 80px); /* tient compte du header si affiché */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}
</style>
