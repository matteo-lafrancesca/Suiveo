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
            <div class="d-flex align-center justify-space-between mb-2">
              <div class="d-flex align-center">
                <v-icon size="18" color="primary" class="mr-2">mdi-phone-check</v-icon>
                <span class="text-subtitle-1 font-weight-bold text-high-emphasis">
                  {{ call.title }}
                </span>
              </div>
              
              <v-chip
                v-if="call.report"
                size="x-small"
                variant="tonal"
                :color="call.report === 'Conforme' ? 'success' : 'error'"
                class="font-weight-bold"
              >
                {{ call.report }}
              </v-chip>
            </div>

            <v-divider class="mb-3 border-opacity-10"></v-divider>

            <div class="text-body-2 text-medium-emphasis">
              {{ call.note?.trim() || "Aucun compte rendu saisi." }}
            </div>
          </div>
        </v-card>
      </v-timeline-item>


      <v-timeline-item
        v-if="nextCall && ['À appeler', 'En retard'].includes(binomeState)"
        :dot-color="binomeState === 'En retard' ? 'error' : 'primary'"
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
              :class="binomeState === 'En retard' ? 'text-error' : 'text-primary'"
            >
              {{ formatDate(nextCall.scheduled_date) }}
            </div>
            <div class="text-caption font-weight-medium" :class="binomeState === 'En retard' ? 'text-error' : 'text-medium-emphasis'">
              {{ binomeState === 'En retard' ? 'En Retard' : 'Prévu' }}
            </div>
          </div>
        </template>

        <v-card 
          class="mb-6 rounded-xl elevation-3 action-card border-l-xl"
          :class="binomeState === 'En retard' ? 'border-error' : 'border-primary'"
        >
          <div class="pa-5">
            <div class="d-flex align-center mb-4">
              <span class="text-h6 font-weight-bold text-high-emphasis">
                {{ nextCall.title }}
              </span>
              <v-spacer />
              <v-btn 
                size="small" 
                variant="text" 
                color="primary" 
                prepend-icon="mdi-calendar-clock"
                @click="$emit('reprogram')"
              >
                Reprogrammer
              </v-btn>
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
import { ref } from "vue";

const props = defineProps({
  events: { type: Array, default: () => [] },
  nextCall: { type: Object, default: null },
  binomeState: { type: String, default: "" },
});

const report = ref("");

function formatDate(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("fr-FR", { day: "2-digit", month: "long", year: "numeric" });
}
</script>

<style scoped>
/* Bordure fine pour un look moderne */
.border-thin {
  border: 1px solid rgba(0,0,0,0.08) !important;
}

/* Bordure gauche épaisse pour la carte d'action */
.border-l-xl {
  border-left-width: 6px !important;
}
.border-primary { border-left-color: rgb(var(--v-theme-primary)) !important; }
.border-error { border-left-color: rgb(var(--v-theme-error)) !important; }

/* Petite animation au survol pour le feedback */
.event-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
}

/* La carte active ne bouge pas, elle est déjà en relief */
.action-card {
  background: white;
}
</style>