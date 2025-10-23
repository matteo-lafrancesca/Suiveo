<template>
  <v-container fluid class="pa-8 content-root">
    <v-row no-gutters class="d-flex align-stretch justify-center">
      <ColonneTableauSuivi
        titre="En Retard"
        icon="mdi-alert"
        :items="enRetard"
      />
      <ColonneTableauSuivi
        titre="À Appeler"
        icon="mdi-phone"
        :items="aAppeler"
      />
      <ColonneTableauSuivi
        titre="Non Conforme"
        icon="mdi-close-circle"
        :items="nonConformes"
      />
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";
import ColonneTableauSuivi from "@/components/ColonneTableauSuivi.vue";

const enRetard = ref([]);
const aAppeler = ref([]);
const nonConformes = ref([]);
const loading = ref(false);

onMounted(async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/binomes/tableau-suivi/");
    enRetard.value = data.en_retard;
    aAppeler.value = data.a_appeler;
    nonConformes.value = data.non_conformes;
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.content-root {
  min-height: calc(100vh - 80px);
  overflow-y: auto;
}
</style>
