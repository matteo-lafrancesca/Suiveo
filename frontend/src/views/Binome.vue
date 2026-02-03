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
                @click="showChangeEmployeeDialog = true"
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
                 @reopen="reopenCall"
                 @deleteManual="deleteManualCall"
               />
            </transition>
            
            <!-- DEBUG : Afficher les appels en attente -->
            <div v-if="pendingCalls.length > 1" class="mt-4 pa-4 bg-grey-lighten-4 rounded">
              <div class="text-caption text-medium-emphasis mb-2">
                📅 Appels programmés ({{ pendingCalls.length }}) :
              </div>
              <div v-for="call in pendingCalls" :key="call.id" class="text-caption">
                • {{ call.title }} - {{ formatDate(call.scheduled_date) }}
              </div>
            </div>
          </div>

          <v-dialog v-model="reprogramDialog" max-width="500px">
            <v-card class="pa-5 rounded-xl">
              <h3 class="text-h6 font-weight-bold mb-1">Reprogrammer l'appel</h3>
              <p class="text-body-2 text-medium-emphasis mb-4">
                L'appel actuel sera archivé et un nouvel appel sera créé.
              </p>
              
              <label class="text-caption font-weight-bold text-medium-emphasis ml-1">Nouvelle date</label>
              <DatePickerField
                v-model="newDate"
                class="mb-2"
              />

              <label class="text-caption font-weight-bold text-medium-emphasis ml-1">Motif (ex: Client absent)</label>
              <v-textarea
                v-model="reprogramReason"
                rows="2"
                auto-grow
                placeholder="Indiquez pourquoi l'appel est reporté..."
                variant="outlined"
                density="comfortable"
                color="primary"
                hide-details
              ></v-textarea>

              <div class="d-flex justify-end mt-4">
                <v-btn variant="text" class="mr-2 rounded-lg" @click="reprogramDialog = false">Annuler</v-btn>
                <v-btn 
                  color="primary" 
                  elevation="0" 
                  class="rounded-lg"
                  :disabled="!newDate"
                  @click="reprogramCall"
                >
                  Valider
                </v-btn>
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
            :first-intervention-date="binome.first_intervention_date"
            @success="fetchBinomeDetails"
          />

          <ChangeEmployeeDialog
            v-model="showChangeEmployeeDialog"
            :binome-id="binome.id"
            :client-id="binome.client.id"
            :current-rhythm="binome.rhythm"
            :current-note="binome.note"
          />

          <!-- Modal de confirmation de suppression -->
          <v-dialog v-model="deleteConfirmDialog" max-width="400">
            <v-card class="rounded-xl">
              <v-card-title class="text-h6 font-weight-bold pa-4 bg-error text-white">
                <v-icon start color="white">mdi-alert-circle</v-icon>
                Confirmer la suppression
              </v-card-title>
              
              <v-card-text class="pa-6">
                <p class="text-body-1 text-medium-emphasis">
                  Voulez-vous vraiment supprimer cet appel manuel ?
                </p>
                <p class="text-caption text-disabled mt-2">
                  Cette action est irréversible.
                </p>
              </v-card-text>

              <v-card-actions class="pa-4 pt-0">
                <v-spacer />
                <v-btn 
                  variant="text" 
                  @click="deleteConfirmDialog = false"
                >
                  Annuler
                </v-btn>
                <v-btn 
                  color="error"
                  variant="elevated"
                  @click="confirmDelete"
                >
                  Supprimer
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>

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
import { useBinomeStore } from "@/stores/binome";
import { getStateColor, getStateIcon } from "@/helpers/binomeHelpers";

// --- IMPORTS COMPOSANTS ---
import BinomeTimeline from "@/components/BinomeTimeline.vue";
import ManualCallDialog from "@/components/ManualCallDialog.vue";
import BinomeNote from "@/components/BinomeNote.vue"; 
import BinomePauseDialog from "@/components/BinomePauseDialog.vue";
import ChangeEmployeeDialog from "@/components/ChangeEmployeeDialog.vue";
import DatePickerField from "@/components/DatePickerField.vue";

const route = useRoute();
const binomeStore = useBinomeStore();

// On utilise computed pour lier les données du store de manière réactive
const binome = computed(() => binomeStore.binome);
const completedCalls = computed(() => binomeStore.completedCalls);
const pendingCalls = computed(() => binomeStore.pendingCalls);
const nextCall = computed(() => binomeStore.nextCall);

const showHistory = ref(false);

// Refs pour Reprogrammation
const reprogramDialog = ref(false);
const newDate = ref("");
const reprogramReason = ref(""); 

// Gestion des Modales (Refs)
const showManualCallDialog = ref(false);
const showPauseDialog = ref(false);
const showChangeEmployeeDialog = ref(false);
const deleteConfirmDialog = ref(false);
const callToDelete = ref(null);

const visibleCalls = computed(() => {
  if (!completedCalls.value || completedCalls.value.length === 0) return [];
  if (showHistory.value) return completedCalls.value;
  return [completedCalls.value[completedCalls.value.length - 1]];
});

async function fetchBinomeDetails() {
  await binomeStore.fetchBinomeDetails(route.params.id);
}

async function markConforme(note) {
  await binomeStore.markConforme(note);
}

async function markNonConforme() {
  await binomeStore.markNonConforme();
}

function openReprogramModal() { 
  // On reset les champs à l'ouverture
  newDate.value = "";
  reprogramReason.value = "";
  reprogramDialog.value = true; 
}

async function reprogramCall() {
  if (!newDate.value || !nextCall.value) return;
  
  try {
    // On envoie la date ET le motif au backend
    await api.post(`/calls/${nextCall.value.id}/reprogrammer/`, { 
      new_date: newDate.value,
      reason: reprogramReason.value 
    });
    
    reprogramDialog.value = false;
    await fetchBinomeDetails();
  } catch (e) {
    console.error("Erreur reprogrammation:", e);
  }
}

async function reopenCall(callId) {
  try {
    await api.post(`/calls/${callId}/reopen/`);
    await fetchBinomeDetails();
  } catch (e) {
    console.error("Erreur réouverture:", e);
  }
}

function deleteManualCall(callId) {
  callToDelete.value = callId;
  deleteConfirmDialog.value = true;
}

async function confirmDelete() {
  if (!callToDelete.value) return;
  
  try {
    await api.delete(`/calls/${callToDelete.value}/`);
    deleteConfirmDialog.value = false;
    callToDelete.value = null;
    await fetchBinomeDetails();
  } catch (e) {
    console.error("Erreur suppression:", e);
  }
}

onMounted(fetchBinomeDetails);

// --- Formatters ---
function formatDate(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("fr-FR", { day: "2-digit", month: "long", year: "numeric" });
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