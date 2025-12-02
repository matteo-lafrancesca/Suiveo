<template>
  <v-container class="pa-8 d-flex justify-center align-center" style="min-height: 80vh">
    <v-card class="pa-6 rounded-xl elevation-2" max-width="500" width="100%">
      <h2 class="text-h6 font-weight-bold mb-6 text-primary">
        Créer un binôme
      </h2>

      <v-alert
        v-if="errorMessage"
        type="error"
        variant="tonal"
        class="mb-4"
        border="start"
      >
        {{ errorMessage }}
      </v-alert>

      <v-form @submit.prevent="submitForm">
        <v-text-field
          v-model="firstIntervention"
          label="Date de première intervention"
          type="date"
          variant="outlined"
          density="comfortable"
          class="mb-4"
          required
        />

        <v-select
          v-model="selectedRhythm"
          :items="rhythmOptions"
          item-title="title"
          item-value="value"
          label="Rythme d'intervention"
          variant="outlined"
          density="comfortable"
          class="mb-4"
          hide-details="auto"
          required
        ></v-select>

        <v-textarea
          v-model="note"
          label="Note sur le binôme (facultative)"
          variant="outlined"
          rows="4"
          auto-grow
          density="comfortable"
          class="mb-6"
        />

        <v-card-actions class="d-flex justify-end">
          <v-btn variant="text" @click="cancel">Annuler</v-btn>
          <v-btn
            color="primary"
            type="submit"
            :disabled="!firstIntervention"
            :loading="loading"
          >
            Valider
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import api from "@/services/api";

const router = useRouter();
const route = useRoute();

const clientId = route.query.client_id;
const employeeId = route.query.employee_id;

const firstIntervention = ref("");
const note = ref("");
// 🆕 Valeur par défaut : 1 (Hebdomadaire)
const selectedRhythm = ref(1);
const loading = ref(false);
const errorMessage = ref("");

// 🆕 Options disponibles
const rhythmOptions = [
  { title: "Hebdomadaire ", value: 1 },
  { title: "Bimensuel", value: 2 },
  { title: "Mensuel", value: 4 },
];

async function submitForm() {
  errorMessage.value = "";
  if (!clientId || !employeeId || !firstIntervention.value) return;

  loading.value = true;
  try {
    await api.post("/binomes/", {
      client_id: clientId,
      employee_id: employeeId,
      first_intervention_date: firstIntervention.value,
      note: note.value,
      // 🆕 Envoi du rythme choisi
      rhythm: selectedRhythm.value,
      state: "Conforme",
    });

    router.push("/liste-binomes");
  } catch (err) {
    console.error("Erreur lors de la création du binôme :", err);
    // 🔹 Si l’API renvoie un message d’erreur clair
    if (err.response?.data?.error) {
      errorMessage.value = err.response.data.error;
    } else {
      errorMessage.value = "Une erreur est survenue lors de la création du binôme.";
    }
  } finally {
    loading.value = false;
  }
}

function cancel() {
  router.push("/creation-gestion");
}
</script>

<style scoped>
.v-card {
  border-top: 3px solid var(--v-primary-base);
}

.text-primary {
  color: #2a4252;
}

.v-btn {
  text-transform: none;
}
</style>