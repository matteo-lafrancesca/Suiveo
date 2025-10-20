<template>
  <v-container fluid class="pa-4 fill-height content-root">
    <v-row no-gutters class="fill-height">

      <!-- === Colonne En Retard === -->
      <v-col cols="12" md="4" class="d-flex flex-column h-100">
        <v-sheet color="background" class="d-flex flex-column flex-grow-1 rounded-lg">
          <!-- Titre -->
          <v-toolbar color="transparent" density="comfortable" class="justify-center">
            <v-icon color="error" class="mr-2">mdi-alert</v-icon>
            <span class="text-h6 font-weight-bold text-error">En Retard</span>
          </v-toolbar>

          <v-divider color="primary" thickness="3" />

          <!-- Contenu scrollable interne -->
          <v-sheet color="background" class="flex-grow-1 overflow-y-auto pa-3">
            <v-card
              v-for="b in enRetard"
              :key="b.id"
              variant="tonal"
              color="error"
              rounded="lg"
              class="mb-3"
            >
              <v-card-title class="d-flex align-center">
                <v-avatar size="36" color="error" class="mr-3">
                  <v-icon color="white">mdi-account-tie</v-icon>
                </v-avatar>
                <div class="font-weight-medium">
                  {{ b.client.last_name }} {{ b.client.first_name }}
                </div>
              </v-card-title>
              <v-card-subtitle>
                Intervenant : {{ b.employee.first_name }} {{ b.employee.last_name }}
              </v-card-subtitle>
            </v-card>
          </v-sheet>
        </v-sheet>
      </v-col>

      <!-- Séparateur vertical -->
      <v-col cols="auto" class="d-none d-md-flex align-stretch">
        <v-divider vertical color="primary" thickness="3"></v-divider>
      </v-col>

      <!-- === Colonne À Appeler === -->
      <v-col cols="12" md="4" class="d-flex flex-column h-100">
        <v-sheet color="background" class="d-flex flex-column flex-grow-1 rounded-lg">
          <v-toolbar color="transparent" density="comfortable" class="justify-center">
            <v-icon color="primary" class="mr-2">mdi-phone</v-icon>
            <span class="text-h6 font-weight-bold text-primary">À Appeler</span>
          </v-toolbar>

          <v-divider color="primary" thickness="3" />

          <v-sheet color="background" class="flex-grow-1 overflow-y-auto pa-3">
            <v-card
              v-for="b in aAppeler"
              :key="b.id"
              variant="tonal"
              color="primary"
              rounded="lg"
              class="mb-3"
            >
              <v-card-title class="d-flex align-center">
                <v-avatar size="36" color="primary" class="mr-3">
                  <v-icon color="white">mdi-account-tie</v-icon>
                </v-avatar>
                <div class="font-weight-medium">
                  {{ b.client.last_name }} {{ b.client.first_name }}
                </div>
              </v-card-title>
              <v-card-subtitle>
                Intervenant : {{ b.employee.first_name }} {{ b.employee.last_name }}
              </v-card-subtitle>
            </v-card>
          </v-sheet>
        </v-sheet>
      </v-col>

      <!-- Séparateur vertical -->
      <v-col cols="auto" class="d-none d-md-flex align-stretch">
        <v-divider vertical color="primary" thickness="3"></v-divider>
      </v-col>

      <!-- === Colonne Non Conforme === -->
      <v-col cols="12" md="4" class="d-flex flex-column h-100">
        <v-sheet color="background" class="d-flex flex-column flex-grow-1 rounded-lg">
          <v-toolbar color="transparent" density="comfortable" class="justify-center">
            <v-icon color="warning" class="mr-2">mdi-close-circle</v-icon>
            <span class="text-h6 font-weight-bold text-warning">Non Conforme</span>
          </v-toolbar>

          <v-divider color="primary" thickness="3" />

          <v-sheet color="background" class="flex-grow-1 overflow-y-auto pa-3">
            <v-card
              v-for="b in nonConformes"
              :key="b.id"
              variant="tonal"
              color="warning"
              rounded="lg"
              class="mb-3"
            >
              <v-card-title class="d-flex align-center">
                <v-avatar size="36" color="warning" class="mr-3">
                  <v-icon color="white">mdi-account-tie</v-icon>
                </v-avatar>
                <div class="font-weight-medium">
                  {{ b.client.last_name }} {{ b.client.first_name }}
                </div>
              </v-card-title>
              <v-card-subtitle>
                Intervenant : {{ b.employee.first_name }} {{ b.employee.last_name }}
              </v-card-subtitle>
            </v-card>
          </v-sheet>
        </v-sheet>
      </v-col>

    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "@/services/api";

const binomes = ref([]);
const loading = ref(false);

const enRetard = computed(() => binomes.value.filter(b => b.state === "En retard"));
const aAppeler = computed(() => binomes.value.filter(b => b.state === "A appeler"));
const nonConformes = computed(() => binomes.value.filter(b => b.state === "Non conforme"));

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
/* La racine occupe tout l’espace disponible sous le header */
.content-root {
  height: 100%;
  overflow: hidden; /* pas de scroll global dans cette zone */
}

/* On peut aussi forcer la colonne à ne jamais dépasser son conteneur */
.v-sheet {
  box-sizing: border-box;
}
</style>
