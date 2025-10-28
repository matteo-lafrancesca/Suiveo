<template>
  <v-container fluid class="pa-8 fill-height content-root">
    <v-row no-gutters class="fill-height d-flex">
      <!-- === Colonne gauche : Fiche Binôme === -->
      <v-col cols="12" md="4" class="pa-3">
        <v-card v-if="binome" class="pa-6 rounded-xl elevation-3" color="surface">
          <v-row align="center" justify="space-between" class="mb-4">
            <v-col cols="auto" class="d-flex align-center">
              <v-avatar size="72" class="mr-4">
                <v-icon size="40" color="primary">mdi-account</v-icon>
              </v-avatar>
              <div>
                <div class="text-h5 font-weight-bold">
                  {{ binome.client.first_name }} {{ binome.client.last_name }}
                </div>
                <div class="text-body-1 text-secondary">Client</div>
              </div>
            </v-col>

            <v-col cols="auto">
              <v-chip
                :color="getStateColor(binome.state)"
                class="px-4 py-2 text-body-1 font-weight-medium chip-opaque"
                label
              >
                <v-icon left size="22" class="mr-1">
                  {{ getStateIcon(binome.state) }}
                </v-icon>
                {{ binome.state }}
              </v-chip>
            </v-col>
          </v-row>

          <v-divider class="my-5" />

          <div class="mb-4">
            <div class="text-subtitle-1 text-secondary mb-1">Intervenant :</div>
            <div class="text-body-1 font-weight-medium">
              {{ binome.employee.first_name }} {{ binome.employee.last_name }}
            </div>
          </div>

          <div class="mb-4">
            <div class="text-subtitle-1 text-secondary mb-1">Date Première Intervention</div>
            <div class="text-body-1 font-weight-medium">
              {{ formatDate(binome.first_intervention_date) }}
            </div>
          </div>

          <div>
            <div class="text-subtitle-1 text-secondary mb-1">Autres informations utiles</div>
            <div class="text-body-1">{{ binome.note || "—" }}</div>
          </div>
        </v-card>

        <v-card v-else class="pa-6 d-flex justify-center align-center elevation-2">
          <v-progress-circular indeterminate color="primary" />
        </v-card>
      </v-col>

      <!-- === Colonne droite : Timeline === -->
      <v-col cols="12" md="8" class="pa-3 d-flex flex-column">
        <div v-if="completedCalls.length || nextCall" class="timeline-scroll">
          <!-- Dernier appel -->
          <BinomeTimeline
            :events="[completedCalls[completedCalls.length - 1]]"
            :nextCall="nextCall"
            :binomeState="binome.state"
          />

          <!-- Bouton pour afficher l’historique -->
          <div v-if="completedCalls.length > 1" class="text-center my-4">
            <v-btn
              variant="text"
              color="primary"
              @click="showHistory = !showHistory"
            >
              {{ showHistory ? "Masquer l’historique" : "Afficher l’historique" }}
              <v-icon end>
                {{ showHistory ? "mdi-chevron-up" : "mdi-chevron-down" }}
              </v-icon>
            </v-btn>
          </div>

          <!-- Historique (anciens appels) -->
          <transition name="fade">
            <div v-if="showHistory">
              <BinomeTimeline
                :events="completedCalls.slice(0, -1)"
                :nextCall="null"
                :binomeState="binome.state"
              />
            </div>
          </transition>
        </div>

        <!-- Modale reprogrammation -->
        <v-dialog v-model="reprogramDialog" max-width="400px">
          <v-card class="pa-4 rounded-lg">
            <h3 class="text-h6 mb-3">Reprogrammer l'appel</h3>
            <v-text-field
              v-model="newDate"
              type="date"
              label="Nouvelle date"
              outlined
            />
            <v-card-actions class="d-flex justify-end mt-3">
              <v-btn variant="text" @click="reprogramDialog = false">
                Annuler
              </v-btn>
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
const reprogramDialog = ref(false);
const newDate = ref("");
const showHistory = ref(false);

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

async function markConforme(note) {
  if (!nextCall.value) return;
  await api.post(`/calls/${nextCall.value.id}/conforme/`, { note });
  await fetchBinomeDetails();
}

async function markNonConforme() {
  if (!nextCall.value) return;
  await api.post(`/calls/${nextCall.value.id}/non-conforme/`);
  await fetchBinomeDetails();
}

function openReprogramModal() {
  reprogramDialog.value = true;
}

async function reprogramCall() {
  if (!newDate.value || !nextCall.value) return;
  await api.post(`/calls/${nextCall.value.id}/reprogrammer/`, {
    new_date: newDate.value,
  });
  reprogramDialog.value = false;
  await fetchBinomeDetails();
}

onMounted(fetchBinomeDetails);

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
    case "Conforme":
      return "success";
    case "Non conforme":
      return "error";
    case "À appeler":
      return "warning";
    case "En retard":
      return "primary";
    default:
      return "grey";
  }
}

function getStateIcon(state) {
  switch (state) {
    case "Conforme":
      return "mdi-check-circle";
    case "Non conforme":
      return "mdi-close-circle";
    case "À appeler":
      return "mdi-phone";
    case "En retard":
      return "mdi-alert";
    default:
      return "mdi-help-circle";
  }
}
</script>

<style scoped>
.v-card {
  border-radius: 16px;
}
.text-secondary {
  color: #6b7280;
}

.timeline-scroll {
  max-height: calc(100vh - 150px);
  overflow-y: auto;
  padding-right: 8px;
  scrollbar-width: thin;
}

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

/* Animation simple pour l’historique */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
