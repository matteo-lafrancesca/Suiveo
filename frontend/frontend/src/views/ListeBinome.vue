<template>
  <v-container fluid class="pa-8 content-root">
    <v-sheet
      color="background"
      class="rounded-xl elevation-2 pa-6"
    >
      <!-- 🔹 Titre -->
      <div class="d-flex justify-space-between align-center mb-6">
        <h1 class="text-h5 font-weight-bold text-primary">
          Liste des Binômes
        </h1>

        <v-progress-circular
          v-if="loading"
          indeterminate
          color="primary"
          size="28"
        />
      </div>

      <!-- 🔹 Tableau principal -->
      <v-data-table
        :headers="headers"
        :items="binomes"
        :loading="loading"
        class="elevation-1 rounded-lg"
        density="comfortable"
        hover
        item-value="id"
        @click:row="goToBinome"
      >
        <template #item.client="{ item }">
          {{ item.client.first_name }} {{ item.client.last_name }}
        </template>

        <template #item.employee="{ item }">
          {{ item.employee.first_name }} {{ item.employee.last_name }}
        </template>

        <template #item.last_call="{ item }">
          <span v-if="item.last_call">
            {{ item.last_call.template?.name || "—" }}
          </span>
          <span v-else>—</span>
        </template>

        <template #item.state="{ item }">
          <v-chip
            :color="getStateColor(item.state)"
            class="text-white font-weight-medium"
            size="small"
            label
          >
            {{ item.state }}
          </v-chip>
        </template>

        <template #item.next_call_week="{ item }">
          <span v-if="item.next_call">
            Semaine {{ getWeekNumber(item.next_call.scheduled_date) }}
          </span>
          <span v-else>—</span>
        </template>

        <!-- Message si aucune donnée -->
        <template #no-data>
          <v-alert color="primary" variant="tonal" class="text-center">
            Aucun binôme trouvé.
          </v-alert>
        </template>
      </v-data-table>
    </v-sheet>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/services/api";
import { format, getWeek } from "date-fns";
import { fr } from "date-fns/locale";
import { useRouter } from "vue-router";

const router = useRouter();
const binomes = ref([]);
const loading = ref(false);

// === En-têtes du tableau ===
const headers = [
  { title: "Client", key: "client", sortable: true },
  { title: "Salarié", key: "employee", sortable: true },
  { title: "Statut d'avancement", key: "last_call", sortable: false },
  { title: "Statut de conformité", key: "state", sortable: true },
  { title: "Semaine du prochain appel", key: "next_call_week", sortable: true },
];

// === Récupération des données ===
onMounted(async () => {
  loading.value = true;
  try {
    const { data } = await api.get("/binomes/");
    binomes.value = await enrichBinomes(data);
  } finally {
    loading.value = false;
  }
});

// === Fonction pour récupérer le dernier appel terminé pour chaque binôme ===
async function enrichBinomes(data) {
  const results = [];

  for (const b of data) {
    const [callsRes] = await Promise.all([
      api.get(`/calls/?binome=${b.id}`),
    ]);

    const calls = callsRes.data;

    // Appel terminé le plus récent
    const lastCall = calls
      .filter((c) => c.actual_date)
      .sort(
        (a, b) =>
          new Date(b.actual_date).getTime() - new Date(a.actual_date).getTime()
      )[0];

    // Prochain appel planifié (sans actual_date)
    const nextCall = calls
      .filter((c) => !c.actual_date)
      .sort(
        (a, b) =>
          new Date(a.scheduled_date).getTime() -
          new Date(b.scheduled_date).getTime()
      )[0];

    results.push({
      ...b,
      last_call: lastCall || null,
      next_call: nextCall || null,
    });
  }

  return results;
}

// === Couleurs selon le statut ===
function getStateColor(state) {
  switch (state) {
    case "Conforme":
      return "success";
    case "Non conforme":
      return "error";
    case "À appeler":
      return "warning";
    case "En retard":
      return "primary";
    default:
      return "grey";
  }
}

// === Semaine d'une date ===
function getWeekNumber(dateStr) {
  return getWeek(new Date(dateStr), { locale: fr });
}

// === Navigation vers la fiche binôme ===
function goToBinome(event, { item }) {
  if (item?.id) router.push(`/binome/${item.id}`);
}
</script>

<style scoped>


.v-data-table {
  background-color: #fff;
  border-radius: 16px;
  overflow: hidden;
}

.v-chip {
  color: white;
}

.v-alert {
  border-radius: 12px;
}
</style>
