<template>
  <div>
    <v-timeline align="start" side="end" density="compact" line-color="grey-lighten-2" truncate-line="both">
      
      <v-timeline-item
        v-for="call in events"
        :key="call.id"
        dot-color="grey-lighten-1"
        fill-dot
        size="small"
        width="100%"
      >
        <template #icon>
          <v-icon size="14" color="white">mdi-check</v-icon>
        </template>

        <template #opposite>
          <div class="text-right pr-4">
            <div class="text-caption font-weight-bold text-medium-emphasis text-uppercase">
              {{ formatDate(call.actual_date || call.scheduled_date) }}
            </div>
            <div class="text-caption text-disabled">Terminé</div>
          </div>
        </template>

        <v-card class="mb-4 rounded-lg elevation-1 border-thin event-card" color="white">
          <div class="pa-4">
            <div class="d-flex align-start justify-space-between mb-2">
              
              <div class="d-flex flex-column flex-grow-1">
                <div class="d-flex align-center">
                  <v-icon size="18" color="primary" class="mr-2">mdi-phone-check</v-icon>
                  <span class="text-subtitle-1 font-weight-bold text-high-emphasis">
                    {{ call.title }}
                  </span>
                </div>

                <div class="text-caption text-medium-emphasis d-flex align-center mt-1 ml-7">
                  <v-icon size="14" start class="mr-1">mdi-calendar-range</v-icon>
                  
                  <span v-if="call.actual_date">
                    <span class="text-high-emphasis font-weight-medium">
                      {{ formatDate(call.actual_date) }}
                    </span>
                    <span class="text-disabled ms-1">
                      (Prévu le {{ formatDate(call.scheduled_date) }})
                    </span>
                  </span>
                  
                  <span v-else>
                    Prévu le {{ formatDate(call.scheduled_date) }}
                  </span>
                </div>
              </div>
              
              <div class="d-flex align-center gap-2">
                <v-chip
                  v-if="call.report"
                  size="x-small"
                  variant="tonal"
                  :color="getReportColor(call.report)"
                  class="font-weight-bold flex-shrink-0"
                >
                  {{ cleanReportText(call.report) }}
                </v-chip>
                
                <!-- Bouton crayon pour rouvrir (seulement sur le dernier appel) -->
                <v-btn
                  v-if="events.indexOf(call) === events.length - 1"
                  size="x-small"
                  variant="text"
                  icon="mdi-pencil"
                  color="grey"
                  @click="$emit('reopen', call.id)"
                >
                  <v-icon size="16">mdi-pencil</v-icon>
                  <v-tooltip activator="parent" location="top">
                    Rouvrir cet appel
                  </v-tooltip>
                </v-btn>
              </div>
            </div>

            <v-divider class="mb-3 border-opacity-10"></v-divider>

            <div class="text-body-2 text-medium-emphasis">
              {{ call.note?.trim() || "Aucun compte rendu saisi." }}
            </div>
          </div>
        </v-card>
      </v-timeline-item>


      <v-timeline-item
        v-if="nextCall && ['À appeler', 'En retard', 'Non conforme'].includes(binomeState)"
        :dot-color="getDotColor(binomeState)"
        fill-dot
        size="default"
        width="100%"
      >
        <template #icon>
          <v-icon size="20" color="white">mdi-phone-in-talk</v-icon>
        </template>

        <template #opposite>
          <div class="text-right pr-4">
            <div 
              class="text-caption font-weight-bold text-uppercase"
              :class="getTextColorClass(binomeState)"
            >
              {{ formatDate(nextCall.scheduled_date) }}
            </div>
            <div class="text-caption font-weight-medium" :class="getTextColorClass(binomeState)">
              {{ getStateLabel(binomeState) }}
            </div>
            
            <!-- Bouton corbeille pour appels manuels -->
            <v-btn
              v-if="isManualCall(nextCall)"
              size="x-small"
              variant="text"
              icon
              color="error"
              class="mt-1"
              @click="$emit('deleteManual', nextCall.id)"
            >
              <v-icon size="16">mdi-delete</v-icon>
              <v-tooltip activator="parent" location="top">
                Supprimer cet appel manuel
              </v-tooltip>
            </v-btn>
          </div>
        </template>

        <v-card 
          class="mb-6 rounded-xl elevation-3 action-card border-l-xl"
          :class="getBorderClass(binomeState)"
        >
          <div class="pa-5">
            <div class="d-flex align-start justify-space-between mb-4">
              
              <div>
                <span class="text-h6 font-weight-bold text-high-emphasis d-block">
                  {{ nextCall.title }}
                </span>
                <div class="text-caption text-medium-emphasis d-flex align-center mt-1">
                  <v-icon size="16" start class="mr-1">mdi-calendar-clock</v-icon>
                  Prévu le {{ formatDate(nextCall.scheduled_date) }}
                </div>
              </div>

              <div class="d-flex gap-2 align-center">
                <!-- Bouton supprimer pour appels manuels -->
                <v-btn 
                  v-if="isManualCall(nextCall)"
                  size="small" 
                  variant="text" 
                  color="error" 
                  prepend-icon="mdi-delete"
                  @click="$emit('deleteManual', nextCall.id)"
                >
                  Supprimer
                </v-btn>
                
                <v-btn 
                  size="small" 
                  variant="text" 
                  color="primary" 
                  prepend-icon="mdi-clock-edit-outline"
                  class="px-0"
                  @click="$emit('reprogram')"
                >
                  Reprogrammer
                </v-btn>
              </div>
            </div>

            <v-textarea
              v-model="report"
              label="Compte-rendu de l'appel..."
              placeholder="Décrivez l'échange avec le client..."
              variant="outlined"
              bg-color="grey-lighten-5"
              color="primary"
              :rows="3"
              auto-grow
              shaped
              class="mb-4"
              hide-details="auto"
            />

            <div class="d-flex justify-end gap-2">
              <v-btn 
                color="error" 
                variant="tonal" 
                class="mr-2"
                prepend-icon="mdi-thumb-down"
                @click="$emit('nonConforme')"
              >
                Non Conforme
              </v-btn>
              <v-btn 
                color="success" 
                elevation="2"
                prepend-icon="mdi-thumb-up"
                @click="$emit('conforme', report)"
              >
                Conforme
              </v-btn>
            </div>
          </div>
        </v-card>
      </v-timeline-item>
    </v-timeline>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  events: { type: Array, default: () => [] },
  nextCall: { type: Object, default: null },
  binomeState: { type: String, default: "" },
});

const report = ref("");

// Vider le champ report quand nextCall change
watch(() => props.nextCall, () => {
  report.value = "";
});

function isManualCall(call) {
  // Utilise directement le champ is_manual du backend
  if (!call) return false;
  return call.is_manual === true;
}

function formatDate(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("fr-FR", { day: "2-digit", month: "long", year: "numeric" });
}

function cleanReportText(text) {
  if (!text) return "";
  return text.split(" — Motif")[0];
}

function getReportColor(text) {
  if (!text) return 'grey';
  if (text.includes('Conforme') && !text.includes('Non')) return 'success';
  if (text.includes('Non conforme')) return 'error';
  if (text.includes('Reprogrammé')) return 'warning';
  return 'grey';
}

function getDotColor(state) {
  if (state === 'En retard') return 'error';
  if (state === 'Non conforme') return 'warning';
  return 'primary';
}

function getTextColorClass(state) {
  if (state === 'En retard') return 'text-error';
  if (state === 'Non conforme') return 'text-warning';
  return 'text-primary';
}

function getBorderClass(state) {
  if (state === 'En retard') return 'border-error';
  if (state === 'Non conforme') return 'border-warning';
  return 'border-primary';
}

function getStateLabel(state) {
  if (state === 'En retard') return 'En Retard';
  if (state === 'Non conforme') return 'Non Conforme - Action Requise';
  return 'Prévu';
}
</script>

<style scoped>
.border-thin { border: 1px solid rgba(0,0,0,0.08) !important; }
.border-l-xl { border-left-width: 6px !important; }
.border-primary { border-left-color: rgb(var(--v-theme-primary)) !important; }
.border-error { border-left-color: rgb(var(--v-theme-error)) !important; }
.border-warning { border-left-color: rgb(var(--v-theme-warning)) !important; }
.event-card { transition: transform 0.2s ease, box-shadow 0.2s ease; }
.event-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important; }
.action-card { background: white; }
</style>