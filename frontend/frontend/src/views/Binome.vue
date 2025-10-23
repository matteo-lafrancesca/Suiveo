<template>
  <v-container fluid class="pa-8 fill-height content-root">
    <v-row no-gutters class="fill-height d-flex">
      <!-- === Colonne gauche : Fiche Binôme === -->
      <v-col cols="12" md="4" class="pa-3">
        <v-card v-if="binome" class="pa-4 rounded-xl elevation-3" color="surface">
          <v-row align="center" justify="space-between" class="mb-2">
            <v-col cols="auto" class="d-flex align-center">
              <v-avatar size="56" class="mr-3">
                <v-icon size="32" color="primary">mdi-account</v-icon>
              </v-avatar>
              <div>
                <div class="text-h6 font-weight-medium">
                  {{ binome.client.first_name }} {{ binome.client.last_name }}
                </div>
                <div class="text-body-2 text-secondary">Client</div>
              </div>
            </v-col>

            <v-col cols="auto" class="d-flex justify-end align-center">
              <v-chip
                :color="getStateColor(binome.state)"
                class="px-3 py-1 text-body-2 font-weight-medium chip-opaque"
                label
              >
                <v-icon left size="18" class="mr-1">{{ getStateIcon(binome.state) }}</v-icon>
                {{ binome.state }}
              </v-chip>
            </v-col>
          </v-row>

          <v-divider class="my-3"></v-divider>

          <div class="mb-2">
            <div class="text-body-2 text-secondary mb-1">Intervenant</div>
            <div class="text-body-1 font-weight-medium">
              {{ binome.employee.first_name }} {{ binome.employee.last_name }}
            </div>
          </div>

          <div class="mb-2">
            <div class="text-body-2 text-secondary mb-1">Première intervention</div>
            <div class="text-body-1 font-weight-medium">
              {{ formatDate(binome.first_intervention_date) }}
            </div>
          </div>

          <div>
            <div class="text-body-2 text-secondary mb-1">Autres informations utiles</div>
            <div class="text-body-1">{{ binome.note || "—" }}</div>
          </div>
        </v-card>

        <v-card v-else class="pa-6 d-flex justify-center align-center elevation-2">
          <v-progress-circular indeterminate color="primary" />
        </v-card>
      </v-col>

      <!-- === Colonne droite : Historique + Next Call === -->
      <v-col cols="12" md="8" class="pa-3 d-flex flex-column">
        <!-- 🔹 Historique des appels avec scroll plus tardif -->
        <div v-if="completedCalls.length" class="timeline-scroll">
          <BinomeTimeline :events="completedCalls" />
        </div>

        <!-- 🔹 Prochain appel (si applicable) -->
        <v-card
          v-if="nextCall && ['À appeler', 'En retard'].includes(binome.state)"
          class="pa-4 rounded-xl elevation-3 mt-8"
        >
          <div class="d-flex align-center mb-3">
            <v-icon color="primary" class="mr-2">mdi-phone</v-icon>
            <span class="text-h6 font-weight-bold">{{ nextCall.title }}</span>
          </div>

          <v-textarea
            v-model="report"
            label="Entrer message Compte–Rendu"
            outlined
            class="mb-4"
          />

          <div class="d-flex justify-space-between">
            <v-btn variant="outlined" color="primary" @click="openReprogramModal">
              Reprogrammer l'appel
            </v-btn>
            <v-btn color="error" @click="markNonConforme">Non Conforme</v-btn>
            <v-btn color="success" @click="markConforme">Conforme</v-btn>
          </div>
        </v-card>

        <!-- Modale reprogrammation -->
        <v-dialog v-model="reprogramDialog" max-width="400px">
          <v-card class="pa-4 rounded-lg">
            <h3 class="text-h6 mb-3">Reprogrammer l'appel</h3>
            <v-text-field v-model="newDate" type="date" label="Nouvelle date" outlined />
            <v-card-actions class="d-flex justify-end mt-3">
              <v-btn variant="text" @click="reprogramDialog = false">Annuler</v-btn>
              <v-btn color="primary" @click="reprogramCall">Valider</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "@/services/api";
import BinomeTimeline from "@/components/BinomeTimeline.vue";

const route = useRoute();
const binome = ref(null);
const completedCalls = ref([]);
const nextCall = ref(null);
const report = ref("");
const reprogramDialog = ref(false);
const newDate = ref("");

function formatDate(dateStr) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  return d.toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

function getStateColor(state) {
  switch (state) {
    case "Conforme": return "success";
    case "Non conforme": return "error";
    case "À appeler": return "warning";
    case "En retard": return "primary";
    default: return "grey";
  }
}

function getStateIcon(state) {
  switch (state) {
    case "Conforme": return "mdi-check-circle";
    case "Non conforme": return "mdi-close-circle";
    case "À appeler": return "mdi-phone";
    case "En retard": return "mdi-alert";
    default: return "mdi-help-circle";
  }
}

async function fetchBinomeDetails() {
  try {
    const id = route.params.id;
    const { data } = await api.get(`/binomes/${id}/details/`);
    binome.value = data.binome;
    completedCalls.value = data.completed_calls || [];
    nextCall.value = data.next_call || null;
  } catch (e) {
    console.error("Erreur chargement binôme :", e);
  }
}

// ✅ Marquer conforme
async function markConforme() {
  if (!nextCall.value) return;
  try {
    await api.post(`/calls/${nextCall.value.id}/conforme/`, { note: report.value });
    await fetchBinomeDetails();
  } catch (e) {
    console.error("Erreur lors de la validation conforme :", e);
  }
}

// ❌ Marquer non conforme
async function markNonConforme() {
  if (!nextCall.value) return;
  try {
    await api.post(`/calls/${nextCall.value.id}/non-conforme/`);
    await fetchBinomeDetails();
  } catch (e) {
    console.error("Erreur lors du passage en non conforme :", e);
  }
}

// 🔄 Reprogrammer appel
function openReprogramModal() {
  reprogramDialog.value = true;
}

async function reprogramCall() {
  if (!newDate.value || !nextCall.value) return;
  try {
    await api.post(`/calls/${nextCall.value.id}/reprogrammer/`, { new_date: newDate.value });
    reprogramDialog.value = false;
    await fetchBinomeDetails();
  } catch (e) {
    console.error("Erreur reprogrammation :", e);
  }
}

onMounted(fetchBinomeDetails);
</script>

<style scoped>
.v-card {
  border-radius: 16px;
}
.text-secondary {
  color: #6b7280;
}
.chip-opaque {
  background-color: #fde68a !important;
  color: #000 !important;
}

/* === Scroll uniquement sur la timeline === */
.timeline-scroll {
  max-height: calc(100vh - 150px); /* plus de place avant le scroll */
  overflow-y: auto;
  padding-right: 8px;
  scrollbar-width: thin;
}

/* Style du scroll (Chrome / Edge) */
.timeline-scroll::-webkit-scrollbar {
  width: 6px;
}
.timeline-scroll::-webkit-scrollbar-thumb {
  background-color: rgba(42, 66, 82, 0.3);
  border-radius: 4px;
}
.timeline-scroll::-webkit-scrollbar-thumb:hover {
  background-color: rgba(42, 66, 82, 0.5);
}
</style>
