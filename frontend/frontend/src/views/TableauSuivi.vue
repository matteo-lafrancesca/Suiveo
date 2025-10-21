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
import { ref, computed, onMounted } from "vue";
import api from "@/services/api";
import ColonneTableauSuivi from "@/components/ColonneTableauSuivi.vue";

const binomes = ref([]);
const loading = ref(false);

const enRetard = computed(() =>
  binomes.value.filter((b) => b.state === "En retard")
);
const aAppeler = computed(() =>
  binomes.value.filter((b) => b.state === "À appeler")
);
const nonConformes = computed(() =>
  binomes.value.filter((b) => b.state === "Non conforme")
);

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
.content-root {
  overflow: hidden;
  height: 100vh;
}
</style>
