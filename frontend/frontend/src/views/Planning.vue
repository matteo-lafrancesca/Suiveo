<template>
  <v-container fluid class="pa-8 content-root">
    <div class="d-flex justify-center align-center mb-6">
      <v-btn icon="mdi-chevron-left" variant="text" color="primary" @click="previousWeek" />
      <div class="d-flex align-center mx-4">
        <span class="text-h5 font-weight-bold text-primary mr-3">Semaine</span>
        <v-text-field
          v-model.number="manualWeek"
          type="number"
          min="1"
          max="53"
          hide-details
          single-line
          variant="outlined"
          density="compact"
          class="week-input mr-3"
          @keydown.enter="goToWeek"
        />
        <span class="text-h6 text-primary">{{ weekRange }}</span>
      </div>
      <v-btn icon="mdi-chevron-right" variant="text" color="primary" @click="nextWeek" />
    </div>

    <v-row no-gutters class="d-flex align-stretch justify-center">
      <ColonnePlanning
        v-for="day in planning.days"
        :key="day.date"
        :titre="day.label"
        :date="day.date"
        :items="day.binomes"
      />
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";
import ColonnePlanning from "@/components/ColonnePlanning.vue";

const planning = ref({ days: [] });
const manualWeek = ref();
const loading = ref(false);
const weekRange = ref("");

async function fetchPlanning(week = null) {
  loading.value = true;
  try {
    const url = week ? `/binomes/planning/?week=${week}` : `/binomes/planning/`;
    const { data } = await api.get(url);
    planning.value = data;
    manualWeek.value = data.week_number;
    weekRange.value = `${new Date(data.monday).toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "short",
    })} → ${new Date(data.friday).toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    })}`;
  } finally {
    loading.value = false;
  }
}

function previousWeek() {
  fetchPlanning(manualWeek.value - 1);
}
function nextWeek() {
  fetchPlanning(manualWeek.value + 1);
}
function goToWeek() {
  fetchPlanning(manualWeek.value);
}

onMounted(() => fetchPlanning());
</script>
