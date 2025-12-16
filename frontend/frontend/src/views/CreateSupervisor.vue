<template>
  <v-container class="fill-height d-flex align-center justify-center">
    <v-card width="500" class="pa-6" elevation="4">
      <v-card-title class="text-h5 font-weight-bold text-center mb-4">
        Inviter un Superviseur
      </v-card-title>

      <v-card-text>
        <v-form @submit.prevent="submit" ref="formRef">
          <v-text-field
            v-model="form.email"
            label="Email"
            type="email"
            variant="outlined"
            density="comfortable"
            class="mb-4"
            :rules="[rules.required, rules.email]"
          ></v-text-field>

          <v-alert
            v-if="error"
            type="error"
            variant="tonal"
            class="mb-4"
            closable
            @click:close="error = null"
          >
            {{ error }}
          </v-alert>

          <v-alert
            v-if="success"
            type="success"
            variant="tonal"
            class="mb-4"
            closable
            @click:close="success = false"
          >
            Invitation envoyée avec succès !
          </v-alert>

          <v-btn
            type="submit"
            color="primary"
            block
            size="large"
            :loading="loading"
          >
            Envoyer l'invitation
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { inviteSupervisor } from '@/services/userService';

const form = ref({
  email: ''
});

const loading = ref(false);
const error = ref(null);
const success = ref(false);

const rules = {
  required: v => !!v || 'Ce champ est requis',
  email: v => /.+@.+\..+/.test(v) || 'Email invalide'
};

async function submit() {
  error.value = null;
  success.value = false;
  
  if (!form.value.email) {
      return;
  }

  loading.value = true;
  try {
    await inviteSupervisor(form.value.email);
    success.value = true;
    form.value = {
      email: ''
    };
  } catch (err) {
    console.error(err);
    if (err.response && err.response.data) {
        error.value = JSON.stringify(err.response.data);
    } else {
        error.value = "Une erreur est survenue lors de l'invitation.";
    }
  } finally {
    loading.value = false;
  }
}
</script>
