<template>
  <v-container fluid class="pa-8 content-root">
    <!-- === Sélecteur de semaine === -->
    <div class="d-flex justify-center align-center mb-6">
      <!-- Bouton précédent -->
      <v-btn
        icon="mdi-chevron-left"
        variant="text"
        color="primary"
        @click="previousWeek"
      />

      <!-- Champ semaine + texte -->
      <div class="d-flex align-center mx-4">
        <span class="text-h5 font-weight-bold text-primary mr-3">Semaine</span>

        <!-- Input semaine -->
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
        ></v-text-field>

        <!-- Période -->
        <span class="text-h6 text-primary">{{ formattedWeekRange }}</span>
      </div>

      <!-- Bouton suivant -->
      <v-btn
        icon="mdi-chevron-right"
        variant="text"
        color="primary"
        @click="nextWeek"
      />
    </div>

    <!-- === Colonnes === -->
    <v-row no-gutters class="d-flex align-stretch justify-center">
      <ColonnePlanning
        v-for="(day, index) in daysOfWeek"
        :key="index"
        :titre="day.label"
        :date="day.date"
        :items="binomesForDay(day.date)"
      />
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import api from "@/services/api";
import ColonnePlanning from "@/components/ColonnePlanning.vue";
import {
  startOfWeek,
  addDays,
  format,
  addWeeks,
  setWeek,
  getWeek,
  setYear,
} from "date-fns";
import { fr } from "date-fns/locale";

// === États ===
const binomes = ref([]);
const loading = ref(false);
const selectedWeek = ref(new Date()); // lundi de la semaine actuelle
const manualWeek = ref(Number(format(new Date(), "w", { locale: fr })));

// === Jours de la semaine ===
const daysOfWeek = computed(() => {
  const start = startOfWeek(selectedWeek.value, { weekStartsOn: 1 });
  return Array.from({ length: 5 }).map((_, i) => ({
    label: format(addDays(start, i), "EEEE dd MMMM", { locale: fr }),
    date: format(addDays(start, i), "yyyy-MM-dd"),
  }));
});

// === Numéro et plage ===
const weekNumber = computed(() =>
  Number(format(selectedWeek.value, "w", { locale: fr }))
);

const formattedWeekRange = computed(() => {
  const start = startOfWeek(selectedWeek.value, { weekStartsOn: 1 });
  const end = addDays(start, 4);
  return `${format(start, "dd MMM", { locale: fr })} → ${format(
    end,
    "dd MMM yyyy",
    { locale: fr }
  )}`;
});

// === Navigation ===
function previousWeek() {
  selectedWeek.value = addWeeks(selectedWeek.value, -1);
}
function nextWeek() {
  selectedWeek.value = addWeeks(selectedWeek.value, 1);
}

// === Aller à la semaine saisie ===
function goToWeek() {
  if (manualWeek.value >= 1 && manualWeek.value <= 53) {
    const year = new Date().getFullYear();
    const newDate = startOfWeek(
      setWeek(setYear(new Date(), year), manualWeek.value),
      { weekStartsOn: 1 }
    );
    selectedWeek.value = newDate;
  }
}

// Met à jour l’input quand on change de semaine par les flèches
watch(weekNumber, (newVal) => {
  manualWeek.value = newVal;
});

// === Filtrage binômes ===
function binomesForDay(dateStr) {
  return binomes.value.filter(
    (b) => b.next_call?.scheduled_date === dateStr
  );
}

// === Chargement API ===
onMounted(async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/binomes/");
    binomes.value = data;
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>


/* === Champ semaine stylisé === */
.week-input {
  width: 80px;
  text-align: center;
}

.week-input input {
  text-align: center;
  font-weight: 600;
  font-size: 1.2rem;
  color: #2a4252;
}

/* Supprime les flèches internes du champ number */
.week-input input::-webkit-inner-spin-button,
.week-input input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
