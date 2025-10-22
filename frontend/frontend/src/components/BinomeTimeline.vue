<template>
  <div class="timeline-wrapper">
    <v-timeline
      align="start"
      side="end"
      density="compact"
      class="timeline-custom"
    >
      <v-timeline-item
        v-for="(event, index) in events"
        :key="index"
        :dot-color="event.type === 'call' ? 'primary' : 'secondary'"
        size="small"
      >
        <template #opposite>
          <div class="text-caption text-secondary">
            {{ formatDate(event.actual_date || event.scheduled_date) }}
          </div>
        </template>

        <!-- Contenu -->
        <div class="timeline-entry">
          <div class="event-title d-flex align-center mb-2">
            <v-icon
              class="mr-2"
              :color="event.type === 'call' ? 'primary' : 'secondary'"
              size="24"
            >
              {{ event.type === 'call' ? 'mdi-phone' : 'mdi-map-marker-check' }}
            </v-icon>
            <span class="font-weight-bold text-primary">
              {{ event.title }}
            </span>
          </div>

          <v-divider class="my-3"></v-divider>

          <div class="event-note">
            {{ event.note || "Aucune note renseignée." }}
          </div>
        </div>
      </v-timeline-item>
    </v-timeline>
  </div>
</template>

<script setup>
const props = defineProps({
  events: {
    type: Array,
    default: () => []
  }
})

function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  })
}
</script>

<style scoped>
.timeline-wrapper {
  background-color: transparent;
  padding-left: 1rem;
}

/* Positionne la timeline bien à gauche */
.timeline-custom {
  justify-content: flex-start;
  margin-left: 0;
}

/* Décale le contenu un peu à droite de la ligne */
.timeline-entry {
  background: transparent;
  padding-left: 2.8rem; /* → décalage vers la droite */
  text-align: left;
  max-width: 95%; /* autorise le texte à s’étaler */
}

/* Titre : un peu plus petit mais toujours lisible */
.event-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #1e293b;
}

/* Note : plus large et plus lisible */
.event-note {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #374151;
  max-width: 100%; /* prend toute la largeur restante */
  word-wrap: break-word;
}

/* Date discrète */
.text-caption {
  font-size: 0.8rem;
  color: #6b7280;
}
</style>
