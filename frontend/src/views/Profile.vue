<template>
  <v-container class="fill-height bg-grey-lighten-5 d-flex justify-center align-center" fluid>
    <v-card class="elevation-2 rounded-xl pa-6" width="100%" max-width="500">
      
      <div class="d-flex flex-column align-center mb-6">
        <v-avatar color="primary" size="80" class="mb-4 text-h4 font-weight-bold elevation-3">
          {{ initials }}
        </v-avatar>
        <h1 class="text-h5 font-weight-bold text-grey-darken-3">{{ user?.first_name }} {{ user?.last_name }}</h1>
        <div class="text-body-2 text-grey-darken-1">{{ user?.email }}</div>
        <v-chip class="mt-2" size="small" color="primary" variant="tonal">{{ user?.role }}</v-chip>
      </div>

      <v-form @submit.prevent="updatePassword">
        <h3 class="text-subtitle-1 font-weight-bold mb-3">Changer de mot de passe</h3>
        
        <v-text-field
            v-model="form.old_password"
            label="Ancien mot de passe"
            variant="outlined"
            density="comfortable"
            rounded="lg"
            type="password"
            prepend-inner-icon="mdi-lock-outline"
            class="mb-2"
        ></v-text-field>

        <v-text-field
            v-model="form.new_password"
            label="Nouveau mot de passe"
            variant="outlined"
            density="comfortable"
            rounded="lg"
            type="password"
            prepend-inner-icon="mdi-lock-plus-outline"
        ></v-text-field>

        <v-alert
          v-if="message"
          :type="messageType"
          variant="tonal"
          class="mt-4 mb-2"
          density="compact"
        >
          {{ message }}
        </v-alert>

        <v-card-actions class="pa-0 mt-6 d-flex flex-column gap-2">
          <v-btn
            block
            color="primary"
            size="large"
            type="submit"
            rounded="lg"
            elevation="1"
            :loading="loading"
            :disabled="!form.old_password || !form.new_password"
          >
            Mettre à jour le mot de passe
          </v-btn>
          
          <v-btn
             block
             variant="text"
             color="grey-darken-1"
             rounded="lg"
             @click="$router.push('/dashboard')"
          >
            Retour au tableau de bord
          </v-btn>
        </v-card-actions>
      </v-form>
      
      <div class="d-flex justify-center mt-6 pt-4 border-t">
          <v-btn 
            variant="text" 
            color="error" 
            size="small" 
            prepend-icon="mdi-logout"
            @click="logout"
          >
            Se déconnecter
          </v-btn>
      </div>

    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import api from '@/services/api';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();
const user = computed(() => authStore.user);

const form = ref({
  old_password: '',
  new_password: ''
});

const loading = ref(false);
const message = ref('');
const messageType = ref('success');

const initials = computed(() => {
  if (!user.value) return '?';
  const f = user.value.first_name?.[0] || '';
  const l = user.value.last_name?.[0] || '';
  return (f + l).toUpperCase() || '?';
});

async function updatePassword() {
  loading.value = true;
  message.value = '';
  
  try {
    // Utilisation d'un endpoint dédié ou PATCH sur /me/ avec logique password
    await api.patch('/me/password/', form.value);
    
    message.value = 'Mot de passe modifié avec succès !';
    messageType.value = 'success';
    
    // Reset form
    form.value.old_password = '';
    form.value.new_password = '';
    
  } catch (e) {
    console.error(e);
    // Gestion d'erreur un peu plus fine
    if (e.response && e.response.data && e.response.data.error) {
        message.value = e.response.data.error;
    } else {
        message.value = 'Erreur lors de la mise à jour (vérifiez votre ancien mot de passe).';
    }
    messageType.value = 'error';
  } finally {
    loading.value = false;
  }
}

function logout() {
    authStore.logout();
    router.push('/login');
}
</script>

<style scoped>
.border-t {
    border-top: 1px solid #eee;
}
.gap-2 {
    gap: 8px;
}
</style>
