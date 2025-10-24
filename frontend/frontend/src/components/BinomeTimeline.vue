<template>
  <div ref="scrollContainer" class="tl-scroll px-4">
    <v-timeline
      class="tl"
      align="start"
      side="end"
      density="compact"
    >
      <!-- === Appels terminés === -->
      <v-timeline-item
        v-for="(call, i) in events"
        :key="call.id"
        dot-color="primary"
        size="small"
        class="call-item"
      >
        <template #opposite>
          <div class="text-caption text-medium-emphasis">
            {{ formatDate(call.actual_date || call.scheduled_date) }}
          </div>
        </template>

        <div>
          <div class="d-flex align-center mb-2">
            <v-icon class="mr-2 tl-icon">mdi-phone</v-icon>
            <span class="text-h6 font-weight-bold text-primary">
              {{ call.title }}
            </span>
          </div>

          <v-divider class="my-3" />

          <div class="text-body-1">
            {{ call.note?.trim() || "Aucun compte rendu disponible." }}
          </div>

          <!-- ✅ Affiche le report du dernier appel
               si binôme conforme OU non conforme -->
          <div
            v-if="
              i === events.length - 1 &&
              call.report &&
              ['Conforme', 'Non conforme'].includes(binomeState)
            "
            class="last-report mt-4"
          >
            <strong>{{ call.report }}</strong>
          </div>
        </div>
      </v-timeline-item>

      <!-- === Prochain appel (nextCall) === -->
      <v-timeline-item
        v-if="nextCall && ['À appeler', 'En retard'].includes(binomeState)"
        dot-color="warning"
        size="small"
        class="call-item"
      >
        <template #opposite>
          <div class="text-caption text-medium-emphasis">
            {{ formatDate(nextCall.scheduled_date) }}
          </div>
        </template>

        <div>
          <div class="d-flex align-center mb-2">
            <v-icon class="mr-2 tl-icon">mdi-phone</v-icon>
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
              <v-btn color="error" class="mr-2" @click="$emit('nonConforme')">
                Non Conforme
              </v-btn>
              <v-btn color="success" @click="$emit('conforme', report)">
                Conforme
              </v-btn>
            </div>
          </div>
        </div>
      </v-timeline-item>
    </v-timeline>

    <!-- Spacer hors timeline -->
    <div aria-hidden="true" class="tl-spacer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from "vue";

const props = defineProps({
  events: { type: Array, default: () => [] },
  nextCall: { type: Object, default: null },
  binomeState: { type: String, default: "" },
});

const report = ref("");
const scrollContainer = ref(null);

function formatDate(dateStr) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  return d.toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
}

async function scrollToBottom() {
  await nextTick();
  const el = scrollContainer.value;
  if (el) el.scrollTop = el.scrollHeight;
}

onMounted(scrollToBottom);
watch(() => [props.events, props.nextCall], scrollToBottom, { deep: true });
</script>

<style scoped>
/* Container scrollable */
.tl-scroll {
  --tl-offset: 150px;
  max-height: calc(100dvh - var(--tl-offset));
  overflow-y: auto;
  padding-right: clamp(6px, 1vw, 16px);
  scroll-behavior: smooth;
}

/* Items espacés et confortables */
.call-item {
  margin-bottom: clamp(40px, 5vh, 80px);
}

.text-h6 {
  font-size: 1.3rem !important;
}

.text-body-1 {
  font-size: 1.1rem !important;
  line-height: 1.6;
}

.last-report {
  font-size: 1.1rem;
  line-height: 1.5;
  font-weight: 600;
  color: var(--v-theme-primary);
}

.tl-icon {
  font-size: clamp(22px, 2.4vh, 30px);
  color: currentColor;
}

/* Spacer en bas pour respirer */
.tl-spacer {
  height: clamp(40vh, 70vh, 110vh);
}

/* Scrollbar */
.tl-scroll::-webkit-scrollbar {
  width: 8px;
}
.tl-scroll::-webkit-scrollbar-thumb {
  background-color: rgba(42, 66, 82, 0.3);
  border-radius: 6px;
}
.tl-scroll::-webkit-scrollbar-thumb:hover {
  background-color: rgba(42, 66, 82, 0.5);
}
</style>
