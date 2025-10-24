<template>
  <v-container fluid class="pa-8 content-root text-center">
    <div class="d-flex justify-center align-center mb-6">
      <v-btn icon="mdi-chevron-left" variant="text" color="primary" @click="previousWeek" />

      <div class="d-flex flex-column align-center mx-4">
        <!-- Ligne principale -->
        <div class="d-flex align-center text-primary text-h5 font-weight-bold">
          <span>Semaine&nbsp;</span>

          <!-- 🗓️ Édition inline sans input -->
          <span
            ref="weekSpan"
            contenteditable="true"
            class="editable-text"
            @blur="onWeekEdit"
            @keydown.enter.prevent="onWeekEdit"
          >
            {{ weekNumber }}
          </span>

          <span class="mx-2">•</span>

          <span
            ref="yearSpan"
            contenteditable="true"
            class="editable-text"
            @blur="onYearEdit"
            @keydown.enter.prevent="onYearEdit"
          >
            {{ year }}
          </span>
        </div>

        <!-- Ligne secondaire -->
        <span class="text-h6 text-medium-emphasis mt-2">{{ weekRange }}</span>
      </div>

      <v-btn icon="mdi-chevron-right" variant="text" color="primary" @click="nextWeek" />
    </div>

    <!-- Contenu -->
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
const weekNumber = ref(0);
const year = ref(new Date().getFullYear());
const weekRange = ref("");

const weekSpan = ref(null);
const yearSpan = ref(null);

async function fetchPlanning(week = null, customYear = null) {
  try {
    const params = new URLSearchParams();
    if (week) params.append("week", week);
    if (customYear) params.append("year", customYear);

    const { data } = await api.get(`/binomes/planning/?${params.toString()}`);
    planning.value = data;
    weekNumber.value = data.week_number;
    year.value = data.year;

    const monday = new Date(data.monday);
    const friday = new Date(data.friday);
    weekRange.value = `${monday.toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "short",
    })} → ${friday.toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "short",
    })}`;
  } catch (e) {
    console.error(e);
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

// ✅ Quand on valide l'édition inline
function onWeekEdit() {
  const val = parseInt(weekSpan.value.innerText.trim());
  if (!isNaN(val) && val >= 1 && val <= 53) {
    fetchPlanning(val, year.value);
  } else {
    weekSpan.value.innerText = weekNumber.value; // Reset si invalide
  }
}
function onYearEdit() {
  const val = parseInt(yearSpan.value.innerText.trim());
  if (!isNaN(val) && val >= 2000 && val <= 2100) {
    fetchPlanning(weekNumber.value, val);
  } else {
    yearSpan.value.innerText = year.value;
  }
}

onMounted(() => fetchPlanning());
</script>

<style scoped>
.editable-text {
  cursor: text;
  display: inline-block;
  min-width: 2ch;
  text-align: center;
  outline: none;
  border-bottom: 1px dashed transparent;
  transition: border-color 0.2s ease;
}
.editable-text:hover {
  border-bottom: 1px dashed var(--v-primary-base);
}
.editable-text:focus {
  border-bottom: 1px solid var(--v-primary-base);
  background-color: transparent;
}
</style>
