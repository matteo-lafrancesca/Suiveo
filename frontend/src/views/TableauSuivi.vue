<template>
  <v-container fluid class="h-screen-offset bg-grey-lighten-4 pa-6 overflow-hidden">
    
    <v-row v-if="loading" class="fill-height d-flex align-center justify-center">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
    </v-row>

    <v-row 
      v-else 
      class="fill-height" 
      align="stretch"
      justify="center" 
      no-gutters
    >
      <v-col cols="12" md="4" class="pa-2 h-100">
        <ColonneTableauSuivi
          titre="En Retard"
          icon="mdi-clock-alert-outline"
          color="grey" 
          :items="enRetard"
        />
      </v-col>

      <v-col cols="12" md="4" class="pa-2 h-100">
        <ColonneTableauSuivi
          titre="À Appeler"
          icon="mdi-phone-in-talk-outline"
          color="warning" 
          :items="aAppeler"
        />
      </v-col>

      <v-col cols="12" md="4" class="pa-2 h-100">
        <ColonneTableauSuivi
          titre="Non Conforme"
          icon="mdi-alert-circle-outline"
          color="error"
          :items="nonConformes"
        />
      </v-col>
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
    enRetard.value = data.en_retard || [];
    aAppeler.value = data.a_appeler || [];
    nonConformes.value = data.non_conformes || [];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
/* Ajustez '64px' si votre barre de navigation (header) a une taille différente.
   Cela permet aux colonnes de descendre jusqu'en bas de l'écran sans dépasser.
*/
.h-screen-offset {
  height: calc(100vh - 64px); 
}
</style>