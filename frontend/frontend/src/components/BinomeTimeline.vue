<template>
  <div class="px-4">
    <v-timeline align="start" side="end" density="compact">
      <v-timeline-item
        v-for="call in events"
        :key="call.id"
        dot-color="primary"
        size="small"
        class="mb-10"
      >
        <template #opposite>
          <div class="text-caption text-medium-emphasis">
            {{ formatDate(call.actual_date || call.scheduled_date) }}
          </div>
        </template>

        <div>
          <div class="d-flex align-center mb-2">
            <v-icon class="mr-2">mdi-phone</v-icon>
            <span class="text-h6 font-weight-bold text-primary">
              {{ call.title }}
            </span>
          </div>

          <v-divider class="my-3" />

          <div class="text-body-1">
            {{ call.note?.trim() || "Aucun compte rendu disponible." }}
          </div>

          <div
            v-if="call.report && ['Conforme', 'Non conforme'].includes(binomeState)"
            class="mt-4 text-body-1 font-weight-bold text-primary"
          >
            {{ call.report }}
          </div>
        </div>
      </v-timeline-item>

      <v-timeline-item
        v-if="nextCall && ['À appeler', 'En retard'].includes(binomeState)"
        dot-color="warning"
        size="small"
        class="mb-10"
      >
        <template #opposite>
          <div class="text-caption text-medium-emphasis">
            {{ formatDate(nextCall.scheduled_date) }}
          </div>
        </template>

        <div>
          <div class="d-flex align-center mb-2">
            <v-icon class="mr-2 text-warning">mdi-phone</v-icon>
            <span class="text-h6 font-weight-bold text-warning">
              {{ nextCall.title }}
            </span>
          </div>

          <v-divider class="my-3" />

          <v-textarea
            v-model="report"
            label="Entrer le compte–rendu de l'appel"
            variant="outlined"
            :rows="3"
            class="mb-3"
          />

          <div class="d-flex justify-space-between">
            <v-btn variant="outlined" color="primary" @click="$emit('reprogram')">
              Reprogrammer
            </v-btn>

            <div>
              <v-btn color="error" class="mr-2" @click="$emit('nonConforme')">Non Conforme</v-btn>
              <v-btn color="success" @click="$emit('conforme', report)">Conforme</v-btn>
            </div>
          </div>
        </div>
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
  const d = new Date(dateStr);
  return d.toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}
</script>
