<template>
  <v-container fluid class="h-screen-offset bg-grey-lighten-4 pa-6 overflow-hidden d-flex flex-column">
    
    <div class="d-flex justify-center align-center mb-4 flex-shrink-0">
      <v-btn 
        icon="mdi-chevron-left" 
        variant="tonal" 
        size="small" 
        color="grey-darken-2" 
        @click="previousWeek" 
      />

      <div class="d-flex flex-column align-center mx-6">
        <div class="d-flex align-center text-h5 font-weight-bold text-grey-darken-3">
          <span class="mr-2">Semaine</span>
          <span
            ref="weekSpan"
            contenteditable="true"
            class="editable-text text-primary"
            @blur="onWeekEdit"
            @keydown.enter.prevent="$event.target.blur()"
          >
            {{ weekNumber }}
          </span>
          <span class="mx-3 text-grey-lighten-1">•</span>
          <span
            ref="yearSpan"
            contenteditable="true"
            class="editable-text text-primary"
            @blur="onYearEdit"
            @keydown.enter.prevent="$event.target.blur()"
          >
            {{ year }}
          </span>
        </div>
        <div class="d-flex align-center mt-1">
            <v-icon size="14" color="grey" class="mr-1">mdi-calendar-range</v-icon>
            <span class="text-caption text-uppercase font-weight-bold text-grey">{{ weekRange }}</span>
        </div>
      </div>

      <v-btn 
        icon="mdi-chevron-right" 
        variant="tonal" 
        size="small" 
        color="grey-darken-2" 
        @click="nextWeek" 
      />
    </div>

    <div v-if="loading" class="d-flex justify-center align-center flex-grow-1">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </div>

    <div 
        v-else 
        class="d-flex flex-grow-1 w-100" 
        style="gap: 16px; overflow-x: auto; min-height: 0;"
    >
      <ColonnePlanning
        v-for="day in planning.days"
        :key="day.date"
        :titre="day.label"
        :date="day.date"
        :items="day.binomes"
      />
    </div>

  </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";
import ColonnePlanning from "@/components/ColonnePlanning.vue";

const planning = ref({ days: [] });
const weekNumber = ref(0);
const year = ref(new Date().getFullYear());
const weekRange = ref("");
const loading = ref(false);
const weekSpan = ref(null);
const yearSpan = ref(null);

// ... (Garder les fonctions fetchPlanning, previousWeek, etc. identiques au code précédent)
// Je remets les fonctions pour que tu puisses copier-coller tout le bloc si besoin

async function fetchPlanning(week = null, customYear = null) {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    if (week) params.append("week", week);
    if (customYear) params.append("year", customYear);

    const { data } = await api.get(`/binomes/planning/?${params.toString()}`);
    
    planning.value = data || { days: [] };
    if(data.week_number) weekNumber.value = data.week_number;
    if(data.year) year.value = data.year;

    if (data.monday && data.friday) {
        const monday = new Date(data.monday);
        const friday = new Date(data.friday);
        weekRange.value = `${monday.toLocaleDateString("fr-FR", { day: "numeric", month: "short" })} - ${friday.toLocaleDateString("fr-FR", { day: "numeric", month: "short" })}`;
    }
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

function previousWeek() {
  let prev = weekNumber.value - 1;
  let prevYear = year.value;
  if (prev < 1) {
    prev = 52;
    prevYear -= 1;
  }
  fetchPlanning(prev, prevYear);
}

function nextWeek() {
  let next = weekNumber.value + 1;
  let nextYear = year.value;
  if (next > 52) {
    next = 1;
    nextYear += 1;
  }
  fetchPlanning(next, nextYear);
}

function onWeekEdit(e) {
  const val = parseInt(e.target.innerText.trim());
  if (!isNaN(val) && val >= 1 && val <= 53) {
    fetchPlanning(val, year.value);
  } else {
    e.target.innerText = weekNumber.value;
  }
}

function onYearEdit(e) {
  const val = parseInt(e.target.innerText.trim());
  if (!isNaN(val) && val >= 2000 && val <= 2100) {
    fetchPlanning(weekNumber.value, val);
  } else {
    e.target.innerText = year.value;
  }
}

onMounted(() => fetchPlanning());
</script>

<style scoped>
/* Ajuste '64px' selon la hauteur de ton Header global (logo Suiveo, profil, etc.) */
.h-screen-offset {
  height: calc(100vh - 64px); 
}

.editable-text {
  cursor: pointer;
  padding: 0 4px;
  border-radius: 4px;
  transition: all 0.2s;
  min-width: 2ch;
  display: inline-block;
  text-align: center;
}
.editable-text:hover {
  background-color: rgba(var(--v-theme-primary), 0.1);
}
.editable-text:focus {
  outline: 2px solid rgb(var(--v-theme-primary));
  background-color: white;
}
</style>