<template>
  <v-sheet
    class="d-flex align-center justify-center"
    color="background"
    height="100vh"
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

      <v-form @submit.prevent="login">
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
        >
          Se connecter
        </v-btn>
      </v-form>
    </v-card>
  </v-sheet>
</template>

<script setup>
import { ref } from 'vue'
const email = ref('')
const password = ref('')
const login = () => console.log(email.value, password.value)
</script>
