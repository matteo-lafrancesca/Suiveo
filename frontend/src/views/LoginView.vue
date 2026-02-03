<template>
  <v-container fluid class="fill-height bg-grey-lighten-5">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" lg="4">

        <v-card class="rounded-xl elevation-0 border-thin pa-6 pa-md-8 bg-white">
          <!-- En-tête avec Logo/Icône -->
          <div class="d-flex flex-column align-center mb-8">
            <v-avatar color="teal-lighten-5" size="64" class="mb-4">
              <v-icon color="teal-darken-3" size="32">mdi-shield-check</v-icon>
            </v-avatar>
            <h1 class="text-h5 font-weight-bold text-grey-darken-3">Bon retour !</h1>
            <p class="text-body-2 text-grey">Connectez-vous pour gérer vos binômes</p>
          </div>

          <v-form @submit.prevent="handleLogin">
            <div class="text-subtitle-2 text-grey-darken-1 mb-1 font-weight-medium">Email</div>
            <v-text-field v-model="email" placeholder="exemple@email.com" prepend-inner-icon="mdi-email-outline"
              variant="outlined" density="comfortable" color="teal-darken-3" bg-color="grey-lighten-5"
              class="rounded-lg mb-2" rounded="lg"></v-text-field>

            <v-text-field v-model="password" placeholder="••••••••" prepend-inner-icon="mdi-lock-outline"
              :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'" :type="showPassword ? 'text' : 'password'"
              @click:append-inner="showPassword = !showPassword" variant="outlined" density="comfortable"
              color="teal-darken-3" bg-color="grey-lighten-5" class="rounded-lg mb-6" rounded="lg"></v-text-field>

            <v-btn type="submit" color="teal-darken-3" block height="48"
              class="text-capitalize font-weight-bold rounded-lg text-body-1" elevation="2" :loading="loading">
              Se connecter
            </v-btn>

            <!-- Zone d'erreur -->
            <v-expand-transition>
              <div v-if="error"
                class="d-flex align-center justify-center mt-4 py-2 bg-red-lighten-5 rounded-lg text-red-darken-2 text-body-2">
                <v-icon size="small" class="mr-2">mdi-alert-circle-outline</v-icon>
                {{ error }}
              </div>
            </v-expand-transition>
          </v-form>
        </v-card>


      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const email = ref("");
const password = ref("");
const showPassword = ref(false); // Pour basculer la visibilité
const error = ref("");
const loading = ref(false);

const handleLogin = async () => {
  error.value = "";
  loading.value = true;

  try {
    await authStore.login(email.value, password.value);
    router.push("/");
  } catch (err) {
    console.error(err);
    // L'erreur est déjà stockée dans le store ou renvoyée
    error.value = authStore.error || "Email ou mot de passe incorrect.";
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* Vuetify fill-height gère le centrage, mais on s'assure que le fond prend tout l'écran */
.fill-height {
  min-height: 100vh;
}

.border-thin {
  border: 1px solid rgba(0, 0, 0, 0.06) !important;
}

.cursor-pointer {
  cursor: pointer;
}
</style>