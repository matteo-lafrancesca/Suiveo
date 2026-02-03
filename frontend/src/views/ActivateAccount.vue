<template>
  <v-container class="fill-height d-flex align-center justify-center">
    <v-card width="500" class="pa-6" elevation="4">
      <v-card-title class="text-h5 font-weight-bold text-center mb-4">
        Activer votre compte
      </v-card-title>

      <v-card-text>
        <div v-if="checkingToken" class="text-center pa-4">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
            <p class="mt-2">Vérification du lien...</p>
        </div>
        <div v-else-if="tokenError">
            <v-alert type="error" variant="tonal">
                {{ tokenError }}
            </v-alert>
        </div>
        <v-form v-else @submit.prevent="submit" ref="formRef">
          <v-text-field
            v-model="email"
            label="Email"
            variant="outlined"
            density="comfortable"
            class="mb-2"
            readonly
            disabled
          ></v-text-field>

          <v-text-field
            v-model="form.first_name"
            label="Prénom"
            variant="outlined"
            density="comfortable"
            class="mb-2"
            :rules="[rules.required]"
          ></v-text-field>

          <v-text-field
            v-model="form.last_name"
            label="Nom"
            variant="outlined"
            density="comfortable"
            class="mb-2"
            :rules="[rules.required]"
          ></v-text-field>

          <v-text-field
            v-model="form.password"
            label="Mot de passe"
            type="password"
            variant="outlined"
            density="comfortable"
            class="mb-4"
            :rules="[rules.required, rules.min]"
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
          >
            Compte activé avec succès ! Vous allez être redirigé...
          </v-alert>

          <v-btn
            type="submit"
            color="primary"
            block
            size="large"
            :loading="loading"
          >
            Activer
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { activateAccount, checkActivationToken } from '@/services/userService';

const route = useRoute();
const router = useRouter();

const form = ref({
  first_name: '',
  last_name: '',
  password: ''
});
const email = ref('');
const checkingToken = ref(true);
const tokenError = ref(null);

const loading = ref(false);
const error = ref(null);
const success = ref(false);

const rules = {
  required: v => !!v || 'Ce champ est requis',
  min: v => v.length >= 8 || 'Minimum 8 caractères'
};

onMounted(async () => {
    const uid = route.query.uid;
    const token = route.query.token;
    
    if (!uid || !token) {
        tokenError.value = "Lien invalide.";
        checkingToken.value = false;
        return;
    }
    
    try {
        const response = await checkActivationToken(uid, token);
        email.value = response.data.email;
    } catch (err) {
        tokenError.value = "Lien invalide ou expiré.";
    } finally {
        checkingToken.value = false;
    }
});

async function submit() {
  error.value = null;
  
  if (!form.value.first_name || !form.value.last_name || !form.value.password) {
      return;
  }

  const uid = route.query.uid;
  const token = route.query.token;

  loading.value = true;
  try {
    await activateAccount({
        uid,
        token,
        ...form.value
    });
    success.value = true;
    setTimeout(() => {
        router.push('/login');
    }, 2000);
  } catch (err) {
    console.error(err);
    if (err.response && err.response.data) {
        error.value = JSON.stringify(err.response.data);
    } else {
        error.value = "Une erreur est survenue lors de l'activation.";
    }
  } finally {
    loading.value = false;
  }
}
</script>
