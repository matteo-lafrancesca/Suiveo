<template>
  <v-container fluid class="pa-8 content-root">
    <v-card class="card-block">
      <!-- === Titre principal === -->
      <div class="d-flex justify-space-between align-center mb-4">
        <h2 class="section-title">
          <v-icon color="primary" class="mr-2">mdi-account-multiple</v-icon>
          Liste des Binômes
        </h2>

        <div class="d-flex align-center">
          <v-text-field
            v-model="searchQuery"
            placeholder="Rechercher un binôme..."
            density="comfortable"
            hide-details
            variant="outlined"
            prepend-inner-icon="mdi-magnify"
            class="search-bar mr-4"
          />
          <v-progress-circular
            v-if="loading"
            indeterminate
            color="primary"
            size="28"
          />
        </div>
      </div>

      <!-- === Tableau principal === -->
      <div class="table-wrapper">
        <v-data-table
          :headers="headers"
          :items="filteredBinomes"
          :loading="loading"
          class="styled-table"
          density="comfortable"
          hover
          hide-default-footer
        >
          <!-- Client -->
          <template #item.client="{ item }">
            {{ item.client.first_name }} {{ item.client.last_name }}
          </template>

          <!-- Salarié -->
          <template #item.employee="{ item }">
            {{ item.employee.first_name }} {{ item.employee.last_name }}
          </template>

          <!-- Statut d'avancement -->
          <template #item.last_call="{ item }">
            <span v-if="item.last_call">
              {{ item.last_call.template?.name || "—" }}
            </span>
            <span v-else>—</span>
          </template>

          <!-- Statut de conformité -->
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

          <!-- Semaine du prochain appel -->
          <template #item.next_call_week="{ item }">
            <span v-if="item.next_call">
              Semaine {{ getWeekNumber(item.next_call.scheduled_date) }}
            </span>
            <span v-else>—</span>
          </template>

          <!-- Boutons d’action -->
          <template #item.actions="{ item }">
            <div class="d-flex align-center" style="gap: 8px;">
              <v-btn
                icon
                color="primary"
                variant="text"
                @click="goToBinome(item.id)"
              >
                <v-icon>mdi-eye-outline</v-icon>
              </v-btn>

              <v-btn
                icon
                color="error"
                variant="text"
                @click="confirmDelete(item.id)"
              >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </div>
          </template>

          <!-- Aucun binôme -->
          <template #no-data>
            <v-alert color="primary" variant="tonal" class="text-center">
              Aucun binôme trouvé.
            </v-alert>
          </template>
        </v-data-table>
      </div>
    </v-card>

    <!-- === Dialogue confirmation suppression === -->
    <v-dialog v-model="confirmVisible" max-width="380px">
      <v-card class="pa-4 rounded-lg">
        <h3 class="text-h6 mb-4 font-weight-medium text-primary">
          Confirmer la suppression
        </h3>
        <p class="text-body-2 mb-6">
          Êtes-vous sûr de vouloir supprimer ce binôme ? Cette action est irréversible.
        </p>
        <v-card-actions class="d-flex justify-end">
          <v-btn variant="text" @click="confirmVisible = false">Annuler</v-btn>
          <v-btn color="error" @click="deleteConfirmed">Supprimer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import api from "@/services/api";
import { getWeek } from "date-fns";
import { fr } from "date-fns/locale";
import { useRouter } from "vue-router";

const router = useRouter();
const binomes = ref([]);
const loading = ref(false);
const searchQuery = ref("");

// === Suppression ===
const confirmVisible = ref(false);
const targetBinomeId = ref(null);

function confirmDelete(id) {
  targetBinomeId.value = id;
  confirmVisible.value = true;
}

async function deleteConfirmed() {
  if (!targetBinomeId.value) return;
  confirmVisible.value = false;
  await api.delete(`/binomes/${targetBinomeId.value}/`);
  await fetchBinomes();
}

// === En-têtes du tableau ===
const headers = [
  { title: "Client", key: "client", sortable: true },
  { title: "Salarié", key: "employee", sortable: true },
  { title: "Statut d'avancement", key: "last_call", sortable: false },
  { title: "Statut de conformité", key: "state", sortable: true },
  { title: "Semaine du prochain appel", key: "next_call_week", sortable: true },
  { title: "", key: "actions", sortable: false },
];

// === Récupération des données ===
onMounted(fetchBinomes);
async function fetchBinomes() {
  loading.value = true;
  try {
    const { data } = await api.get("/binomes/");
    binomes.value = await enrichBinomes(data);
  } finally {
    loading.value = false;
  }
}

// === Enrichissement des données binômes ===
async function enrichBinomes(data) {
  const results = [];
  for (const b of data) {
    const [callsRes] = await Promise.all([api.get(`/calls/?binome=${b.id}`)]);
    const calls = callsRes.data;

    const lastCall = calls
      .filter((c) => c.actual_date)
      .sort((a, b) => new Date(b.actual_date) - new Date(a.actual_date))[0];

    const nextCall = calls
      .filter((c) => !c.actual_date)
      .sort((a, b) => new Date(a.scheduled_date) - new Date(b.scheduled_date))[0];

    results.push({
      ...b,
      last_call: lastCall || null,
      next_call: nextCall || null,
    });
  }
  return results;
}

// === Filtrage recherche ===
const filteredBinomes = computed(() => {
  const query = searchQuery.value.toLowerCase().trim();
  if (!query) return binomes.value;

  return binomes.value.filter((b) => {
    const client = `${b.client.first_name} ${b.client.last_name}`.toLowerCase();
    const employee = `${b.employee.first_name} ${b.employee.last_name}`.toLowerCase();
    const state = b.state?.toLowerCase() || "";
    const lastCall = b.last_call?.template?.name?.toLowerCase() || "";
    const nextWeek = b.next_call
      ? `semaine ${getWeekNumber(b.next_call.scheduled_date)}`.toLowerCase()
      : "";

    return (
      client.includes(query) ||
      employee.includes(query) ||
      state.includes(query) ||
      lastCall.includes(query) ||
      nextWeek.includes(query)
    );
  });
});

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

// === Navigation ===
function goToBinome(id) {
  router.push(`/binome/${id}`);
}
</script>

<style scoped>
/* === Cartes principales === */
.card-block {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 24px;
  border-top: 3px solid var(--v-primary-base);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

/* === Titre de section === */
.section-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #2a4252;
}

/* === Barre de recherche === */
.search-bar {
  background-color: #fff;
  border-radius: 8px;
  width: 300px;
}

/* === Tableau === */
.table-wrapper {
  max-height: 65vh;
  overflow-y: auto;
}

.styled-table {
  border-radius: 8px;
  background-color: #fff;
}

.styled-table tbody tr:hover {
  background-color: rgba(42, 66, 82, 0.05);
}

/* === Boutons d’action === */
.v-btn {
  transition: background 0.2s ease;
}

.v-btn:hover {
  background-color: rgba(42, 66, 82, 0.1);
}

/* === Alerte "aucune donnée" === */
.v-alert {
  border-radius: 12px;
}
</style>
