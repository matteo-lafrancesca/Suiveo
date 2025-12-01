<template>
  <v-container fluid class="pa-8 fill-height bg-grey-lighten-5 overflow-hidden">
    <v-row class="fill-height d-flex justify-center">
      
      <v-col cols="12" md="4" lg="3" class="pa-3">
        <v-card v-if="binome" class="rounded-xl border-thin" elevation="0" color="white">
          
          <div class="pa-6 bg-grey-lighten-5 d-flex flex-column align-center text-center rounded-t-xl position-relative">
            <v-avatar size="88" class="elevation-2 mb-3 bg-white">
              <v-icon size="48" color="primary">mdi-account</v-icon>
            </v-avatar>
            
            <h2 class="text-h5 font-weight-bold text-high-emphasis">
              {{ binome.client.first_name }} {{ binome.client.last_name }}
            </h2>
            <div class="text-caption text-uppercase font-weight-bold text-medium-emphasis mt-1">
              Dossier Client
            </div>

            <v-chip
              :color="getStateColor(binome.state)"
              class="mt-3 font-weight-bold"
              size="small"
              variant="flat"
            >
              <v-icon start size="16">{{ getStateIcon(binome.state) }}</v-icon>
              {{ binome.state }}
            </v-chip>
          </div>

          <v-divider></v-divider>

          <div class="pa-6">
            
            <div class="d-flex align-start mb-6">
              <v-avatar color="primary" variant="tonal" size="40" class="mr-3 rounded-lg">
                <v-icon>mdi-briefcase-account</v-icon>
              </v-avatar>
              <div>
                <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold">Intervenant</div>
                <div class="text-body-1 font-weight-medium">
                  {{ binome.employee.first_name }} {{ binome.employee.last_name }}
                </div>
              </div>
            </div>

            <div class="d-flex align-start mb-6">
              <v-avatar color="secondary" variant="tonal" size="40" class="mr-3 rounded-lg">
                <v-icon>mdi-calendar-start</v-icon>
              </v-avatar>
              <div>
                <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold">Début Intervention</div>
                <div class="text-body-1 font-weight-medium">
                  {{ formatDate(binome.first_intervention_date) }}
                </div>
              </div>
            </div>

            <BinomeNote 
              :binome-id="binome.id"
              :note="binome.note"
              @update:note="binome.note = $event"
            />

            <div>
              <div class="text-caption text-medium-emphasis text-uppercase font-weight-bold mb-3">
                Actions rapides
              </div>

              <v-btn
                block
                color="primary"
                variant="tonal"
                class="mb-2 justify-start"
                rounded="lg"
                prepend-icon="mdi-phone-plus"
                @click="showManualCallDialog = true"
              >
                Programmer un appel
              </v-btn>

              <v-btn
                block
                color="orange-darken-1"
                variant="tonal"
                class="mb-2 justify-start"
                rounded="lg"
                prepend-icon="mdi-pause-circle-outline"
                @click="showPauseDialog = true"
              >
                Programmer une pause
              </v-btn>

              <v-btn
                block
                color="blue-grey"
                variant="tonal"
                class="justify-start"
                rounded="lg"
                prepend-icon="mdi-account-switch-outline"
                @click="openChangeEmployee"
              >
                Changer d'intervenant
              </v-btn>
            </div>
          </div>
        </v-card>

        <v-card v-else class="pa-12 d-flex justify-center align-center rounded-xl elevation-0 border-thin" height="400">
          <v-progress-circular indeterminate color="primary" size="64" width="6" />
        </v-card>
      </v-col>

      <v-col cols="12" md="8" lg="7" class="pa-3 d-flex flex-column" style="max-height: 100%;">
        
        <template v-if="binome">
          
          <div v-if="completedCalls.length > 1" class="d-flex justify-center mb-2 flex-shrink-0">
            <v-btn
              variant="text"
              rounded="pill"
              color="primary"
              class="text-caption font-weight-bold px-6"
              @click="showHistory = !showHistory"
            >
              <v-icon start class="mr-1">
                {{ showHistory ? "mdi-chevron-up" : "mdi-history" }}
              </v-icon>
              {{ showHistory ? "Masquer l'historique" : "Afficher l'historique complet" }}
            </v-btn>
          </div>

          <div class="timeline-container px-2">
            <transition name="fade" mode="out-in">
              <BinomeTimeline
                 :key="showHistory ? 'full' : 'short'"
                 :events="visibleCalls"
                 :nextCall="nextCall"
                 :binomeState="binome?.state" 
                 @conforme="markConforme"
                 @nonConforme="markNonConforme"
                 @reprogram="openReprogramModal"
               />
            </transition>
          </div>

          <v-dialog v-model="reprogramDialog" max-width="400px">
            <v-card class="pa-5 rounded-xl">
              <h3 class="text-h6 font-weight-bold mb-1">Reprogrammer</h3>
              <p class="text-body-2 text-medium-emphasis mb-4">Choisissez une nouvelle date pour cet appel.</p>
              <v-text-field
                v-model="newDate"
                type="date"
                variant="outlined"
                density="comfortable"
                color="primary"
              />
              <div class="d-flex justify-end mt-2">
                <v-btn variant="text" class="mr-2" @click="reprogramDialog = false">Annuler</v-btn>
                <v-btn color="primary" elevation="0" @click="reprogramCall">Valider</v-btn>
              </div>
            </v-card>
          </v-dialog>

          <ManualCallDialog 
            v-model="showManualCallDialog"
            :binome-id="binome.id"
            @success="fetchBinomeDetails"
          />

          <BinomePauseDialog
            v-model="showPauseDialog"
            :binome-id="binome.id"
            @success="fetchBinomeDetails"
          />

        </template>

        <div v-else class="d-flex justify-center align-center fill-height">
          <v-progress-circular indeterminate color="primary" />
        </div>

      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import api from "@/services/api";

// --- IMPORTS COMPOSANTS ---
import BinomeTimeline from "@/components/BinomeTimeline.vue";
import ManualCallDialog from "@/components/ManualCallDialog.vue";
import BinomeNote from "@/components/BinomeNote.vue"; 
import BinomePauseDialog from "@/components/BinomePauseDialog.vue"; // <--- Import

const route = useRoute();
const binome = ref(null);
const completedCalls = ref([]);
const nextCall = ref(null);
const showHistory = ref(false);

const reprogramDialog = ref(false);
const newDate = ref("");

// Gestion des Modales
const showManualCallDialog = ref(false);
const showPauseDialog = ref(false); // <--- Nouvelle ref

const visibleCalls = computed(() => {
  if (!completedCalls.value || completedCalls.value.length === 0) return [];
  if (showHistory.value) return completedCalls.value;
  return [completedCalls.value[completedCalls.value.length - 1]];
});

async function fetchBinomeDetails() {
  try {
    const id = route.params.id;
    const { data } = await api.get(`/binomes/${id}/details/`);
    binome.value = data.binome;
    completedCalls.value = data.completed_calls || [];
    nextCall.value = data.next_call || null;
  } catch (e) { console.error(e); }
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

function openReprogramModal() { reprogramDialog.value = true; }

async function reprogramCall() {
  if (!newDate.value || !nextCall.value) return;
  await api.post(`/calls/${nextCall.value.id}/reprogrammer/`, { new_date: newDate.value });
  reprogramDialog.value = false;
  await fetchBinomeDetails();
}

// --- Placeholders ---
function openChangeEmployee() { console.log("TODO: Change Employee"); }

onMounted(fetchBinomeDetails);

// --- Formatters ---
function formatDate(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("fr-FR", { day: "2-digit", month: "long", year: "numeric" });
}

function getStateColor(state) {
  switch (state) {
    case "Conforme": return "success";
    case "Non conforme": return "error";
    case "À appeler": return "warning";
    case "En retard": return "error";
    default: return "grey";
  }
}

function getStateIcon(state) {
  switch (state) {
    case "Conforme": return "mdi-check-circle";
    case "Non conforme": return "mdi-close-circle";
    case "À appeler": return "mdi-phone";
    case "En retard": return "mdi-clock-alert";
    default: return "mdi-help-circle";
  }
}
</script>

<style scoped>
.timeline-container {
  flex: 1 1 auto;
  overflow-y: auto;
  min-height: 0;
  padding-bottom: 3rem !important;
}
.timeline-container::-webkit-scrollbar { width: 6px; }
.timeline-container::-webkit-scrollbar-thumb { background-color: #e0e0e0; border-radius: 4px; }

/* Transitions */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease, transform 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-10px); }
</style>