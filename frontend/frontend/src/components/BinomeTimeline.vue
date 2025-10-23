<template>
  <div class="timeline-wrapper">
    <v-timeline align="start" side="end" density="compact" class="timeline-custom">
      <v-timeline-item
        v-for="(call, index) in sortedEvents"
        :key="index"
        dot-color="primary"
        size="small"
      >
        <!-- Date à gauche -->
        <template #opposite>
          <div class="text-caption text-secondary">
            {{ formatDate(call.actual_date || call.scheduled_date) }}
          </div>
        </template>

        <!-- Contenu principal -->
        <div class="timeline-entry">
          <!-- Titre -->
          <div class="event-title d-flex align-center mb-2">
            <v-icon class="mr-2 flex-shrink-0" color="primary" size="24">mdi-phone</v-icon>
            <span class="font-weight-bold text-primary event-title-text">
              {{ call.title }}
            </span>
          </div>

          <v-divider class="my-3"></v-divider>

          <!-- Compte rendu -->
          <div class="event-note">
            {{ call.note?.trim() || "Aucun compte rendu disponible." }}
          </div>
        </div>
      </v-timeline-item>
    </v-timeline>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  events: {
    type: Array,
    default: () => [],
  },
});

const sortedEvents = computed(() =>
  [...props.events].sort(
    (a, b) =>
      new Date(a.actual_date || a.scheduled_date) -
      new Date(b.actual_date || b.scheduled_date)
  )
);

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}
</script>

<style scoped>
.timeline-wrapper {
  background-color: transparent;
  padding-left: 1rem;
}

.timeline-custom {
  justify-content: flex-start;
  margin-left: 0;
}

.timeline-entry {
  background: transparent;
  padding-left: 2.8rem;
  text-align: left;
  max-width: 100%;
}

/* Titre bien visible et large */
.event-title-text {
  font-size: 1.4rem;
  font-weight: 700;
  color: #1e293b;
  white-space: normal;
  word-break: break-word;
  flex: 1;
}

/* Compte rendu */
.event-note {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #374151;
  white-space: pre-line;
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-width: 95%;
}

.text-caption {
  font-size: 0.8rem;
  color: #6b7280;
}
</style>
