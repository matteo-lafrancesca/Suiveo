<template>
  <v-container fluid class="pa-8 content-root">
    <!-- === Deux tableaux côte à côte === -->
    <v-row dense>
      <!-- === Clients === -->
      <v-col cols="12" md="6">
        <v-card class="card-block">
          <div class="d-flex justify-space-between align-center mb-4">
            <h2 class="section-title">
              <v-icon color="primary" class="mr-2">mdi-account</v-icon> Clients
            </h2>

            <div class="d-flex align-center">
              <v-text-field
                v-model="searchClient"
                placeholder="Rechercher un client..."
                density="comfortable"
                hide-details
                variant="outlined"
                prepend-inner-icon="mdi-magnify"
                class="search-bar mr-3"
              />
              <v-btn color="primary" prepend-icon="mdi-plus" @click="openDialog('client')">
                Nouveau
              </v-btn>
            </div>
          </div>

          <div class="table-wrapper">
            <v-data-table
              :headers="clientHeaders"
              :items="filteredClients"
              density="comfortable"
              hover
              hide-default-footer
              class="styled-table"
            >
              <template #item.actions="{ item }">
                <v-btn
                  icon
                  variant="text"
                  @click="confirmDelete('client', item.id)"
                  class="delete-btn"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>

              <template #no-data>
                <v-alert color="primary" variant="tonal" class="text-center">
                  Aucun client trouvé.
                </v-alert>
              </template>
            </v-data-table>
          </div>
        </v-card>
      </v-col>

      <!-- === Salariés === -->
      <v-col cols="12" md="6">
        <v-card class="card-block">
          <div class="d-flex justify-space-between align-center mb-4">
            <h2 class="section-title">
              <v-icon color="primary" class="mr-2">mdi-account-tie</v-icon> Salariés
            </h2>

            <div class="d-flex align-center">
              <v-text-field
                v-model="searchEmployee"
                placeholder="Rechercher un salarié..."
                density="comfortable"
                hide-details
                variant="outlined"
                prepend-inner-icon="mdi-magnify"
                class="search-bar mr-3"
              />
              <v-btn color="primary" prepend-icon="mdi-plus" @click="openDialog('employee')">
                Nouveau
              </v-btn>
            </div>
          </div>

          <div class="table-wrapper">
            <v-data-table
              :headers="employeeHeaders"
              :items="filteredEmployees"
              density="comfortable"
              hover
              hide-default-footer
              class="styled-table"
            >
              <template #item.actions="{ item }">
                <v-btn
                  icon
                  variant="text"
                  @click="confirmDelete('employee', item.id)"
                  class="delete-btn"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>

              <template #no-data>
                <v-alert color="primary" variant="tonal" class="text-center">
                  Aucun salarié trouvé.
                </v-alert>
              </template>
            </v-data-table>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- === Création de Binôme === -->
    <v-card class="card-block mt-8">
      <h2 class="section-title mb-4">
        <v-icon color="primary" class="mr-2">mdi-link-variant</v-icon> Créer un binôme
      </h2>

      <div class="d-flex flex-wrap align-center justify-start gap-4">
        <!-- ✅ On charge les clients disponibles (sans binôme existant) -->
        <v-autocomplete
          v-model="selectedClient"
          :items="availableClients"
          item-title="full_name"
          item-value="id"
          label="Sélectionner un client"
          variant="outlined"
          density="comfortable"
          clearable
          hide-details
          class="mr-4"
          style="min-width: 300px"
        />

        <v-autocomplete
          v-model="selectedEmployee"
          :items="employees"
          item-title="full_name"
          item-value="id"
          label="Sélectionner un salarié"
          variant="outlined"
          density="comfortable"
          clearable
          hide-details
          class="mr-4"
          style="min-width: 300px"
        />

        <v-btn
          color="primary"
          prepend-icon="mdi-account-multiple-plus"
          :disabled="!selectedClient || !selectedEmployee"
          @click="goToCreateBinome"
        >
          Associer le binôme
        </v-btn>
      </div>
    </v-card>

    <!-- === Dialogue création client/employé === -->
    <v-dialog v-model="dialogVisible" max-width="400px">
      <v-card class="pa-4 rounded-lg">
        <h3 class="text-h6 font-weight-medium mb-4 text-primary">
          {{ dialogType === 'client' ? 'Ajouter un client' : 'Ajouter un salarié' }}
        </h3>

        <v-text-field
          v-model="firstName"
          label="Prénom"
          variant="outlined"
          density="comfortable"
          class="mb-3"
        />
        <v-text-field
          v-model="lastName"
          label="Nom"
          variant="outlined"
          density="comfortable"
          class="mb-4"
        />

        <v-card-actions class="d-flex justify-end">
          <v-btn variant="text" @click="closeDialog">Annuler</v-btn>
          <v-btn color="primary" @click="createEntry">Créer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- === Dialogue confirmation suppression === -->
    <v-dialog v-model="confirmVisible" max-width="380px">
      <v-card class="pa-4 rounded-lg">
        <h3 class="text-h6 mb-4 font-weight-medium text-primary">
          Confirmer la suppression
        </h3>
        <p class="text-body-2 mb-6">
          Êtes-vous sûr de vouloir supprimer cet élément ? Cette action est irréversible.
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
import { useRouter } from "vue-router";
import api from "@/services/api";

const router = useRouter();

const clients = ref([]);
const availableClients = ref([]); // 👈 clients sans binôme
const employees = ref([]);
const loading = ref(false);

const searchClient = ref("");
const searchEmployee = ref("");

const dialogVisible = ref(false);
const dialogType = ref(null);
const firstName = ref("");
const lastName = ref("");

// === Sélection pour création binôme ===
const selectedClient = ref(null);
const selectedEmployee = ref(null);

// === Confirmation suppression ===
const confirmVisible = ref(false);
const deleteTarget = ref({ type: null, id: null });

function confirmDelete(type, id) {
  deleteTarget.value = { type, id };
  confirmVisible.value = true;
}

async function deleteConfirmed() {
  const { type, id } = deleteTarget.value;
  confirmVisible.value = false;
  if (type === "client") await api.delete(`/clients/${id}/`);
  if (type === "employee") await api.delete(`/employees/${id}/`);
  await fetchData();
}

// === En-têtes ===
const clientHeaders = [
  { title: "Prénom", key: "first_name" },
  { title: "Nom", key: "last_name" },
  { title: "", key: "actions", sortable: false },
];
const employeeHeaders = [
  { title: "Prénom", key: "first_name" },
  { title: "Nom", key: "last_name" },
  { title: "", key: "actions", sortable: false },
];

// === Filtres recherche ===
const filteredClients = computed(() => {
  const search = searchClient.value.toLowerCase();
  return clients.value.filter(
    (c) =>
      c.first_name.toLowerCase().includes(search) ||
      c.last_name.toLowerCase().includes(search)
  );
});

const filteredEmployees = computed(() => {
  const search = searchEmployee.value.toLowerCase();
  return employees.value.filter(
    (e) =>
      e.first_name.toLowerCase().includes(search) ||
      e.last_name.toLowerCase().includes(search)
  );
});

// === CRUD ===
function openDialog(type) {
  dialogType.value = type;
  dialogVisible.value = true;
}
function closeDialog() {
  dialogVisible.value = false;
  firstName.value = "";
  lastName.value = "";
}

async function createEntry() {
  const endpoint = dialogType.value === "client" ? "/clients/" : "/employees/";
  await api.post(endpoint, {
    first_name: firstName.value,
    last_name: lastName.value,
  });
  closeDialog();
  await fetchData();
}

// === Redirection vers le formulaire de création de binôme ===
function goToCreateBinome() {
  if (!selectedClient.value || !selectedEmployee.value) return;
  router.push({
    path: "/creation-binome",
    query: {
      client_id: selectedClient.value,
      employee_id: selectedEmployee.value,
    },
  });
}

// === Chargement API ===
onMounted(fetchData);
async function fetchData() {
  loading.value = true;
  try {
    // 👇 Charge les clients complets + ceux disponibles
    const [clientsRes, availableRes, employeesRes] = await Promise.all([
      api.get("/clients/"),
      api.get("/clients/disponibles/"),
      api.get("/employees/"),
    ]);

    clients.value = clientsRes.data.map((c) => ({
      ...c,
      full_name: `${c.first_name} ${c.last_name}`,
    }));

    availableClients.value = availableRes.data.map((c) => ({
      ...c,
      full_name: `${c.first_name} ${c.last_name}`,
    }));

    employees.value = employeesRes.data.map((e) => ({
      ...e,
      full_name: `${e.first_name} ${e.last_name}`,
    }));
  } finally {
    loading.value = false;
  }
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

/* === Titres de section === */
.section-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  color: #2a4252;
}

/* === Tableaux === */
.table-wrapper {
  max-height: 52vh;
  overflow-y: auto;
}

.styled-table {
  border-radius: 8px;
}

.styled-table tbody tr:hover {
  background-color: rgba(42, 66, 82, 0.05);
}

/* === Icône suppression === */
.delete-btn {
  color: #94a3b8;
  transition: color 0.2s ease;
}
.delete-btn:hover {
  color: #d94a4a;
}

/* === Barre de recherche === */
.search-bar {
  background-color: #fff;
  border-radius: 8px;
  width: 300px;
}
</style>
