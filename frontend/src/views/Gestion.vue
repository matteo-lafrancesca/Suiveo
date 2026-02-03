<template>
  <v-container fluid class=" d-flex flex-column bg-grey-lighten-5 pa-4 pa-md-6 ">
    
    <v-row class="w-100" dense style="min-height: 0;">
      
      <v-col cols="12" md="6" class="pr-md-3 pb-2 pb-md-0">
        <v-card class="d-flex flex-column rounded-xl elevation-0 border-thin bg-white">
          
          <div class="px-5 py-4 d-flex justify-space-between align-center border-b flex-shrink-0">
            <div class="d-flex align-center">
              <v-avatar color="blue-lighten-5" rounded="lg" class="mr-3" size="40">
                <v-icon color="blue-darken-2" size="24">mdi-account-group</v-icon>
              </v-avatar>
              <div>
                <h3 class="text-subtitle-1 font-weight-bold text-grey-darken-3">Clients</h3>
                <div class="text-caption text-grey font-weight-medium">{{ clients.length }} dossiers</div>
              </div>
            </div>
            <v-btn
              color="blue-darken-1"
              variant="flat"
              size="small"
              class="rounded-lg text-capitalize"
              prepend-icon="mdi-plus"
              @click="openDialog('client')"
            >
              Nouveau
            </v-btn>
          </div>

          <div class="px-4 py-3 bg-white flex-shrink-0">
            <v-text-field
              v-model="searchClient"
              placeholder="Rechercher un client..."
              density="compact"
              variant="outlined"
              hide-details
              prepend-inner-icon="mdi-magnify"
              base-color="grey-lighten-2"
              color="blue"
              bg-color="grey-lighten-5"
              class="rounded-lg"
            ></v-text-field>
          </div>

          <div class="flex-grow-1 overflow-hidden px-2 pb-2">
            <v-data-table
              :headers="clientHeaders"
              :items="filteredClients"
              density="comfortable"
              hover
              fixed-header
              height="60vh"
              class="clean-table"
              items-per-page="-1"
            >
              <template #no-data>
                <div class="py-10 text-center text-grey">Aucun client trouvé</div>
              </template>

              <template #item.first_name="{ item }">
                 <span class="font-weight-medium text-grey-darken-3">{{ item.first_name }}</span>
              </template>
              
              <template #item.actions="{ item }">
                <v-btn icon variant="text" color="grey-lighten-1" size="small" class="delete-hover" @click="confirmDelete('client', item.id)">
                  <v-icon size="20">mdi-trash-can-outline</v-icon>
                </v-btn>
              </template>
              
              <template #bottom></template>
            </v-data-table>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="6" class="pl-md-3 pt-3 pt-md-0">
        <v-card class="d-flex flex-column rounded-xl elevation-0 border-thin bg-white">
          
          <div class="px-5 py-4 d-flex justify-space-between align-center border-b flex-shrink-0">
            <div class="d-flex align-center">
              <v-avatar color="purple-lighten-5" rounded="lg" class="mr-3" size="40">
                <v-icon color="purple-darken-2" size="24">mdi-briefcase-account</v-icon>
              </v-avatar>
              <div>
                <h3 class="text-subtitle-1 font-weight-bold text-grey-darken-3">Salariés</h3>
                <div class="text-caption text-grey font-weight-medium">{{ employees.length }} actifs</div>
              </div>
            </div>
            <v-btn
              color="purple-darken-1"
              variant="flat"
              size="small"
              class="rounded-lg text-capitalize"
              prepend-icon="mdi-plus"
              @click="openDialog('employee')"
            >
              Nouveau
            </v-btn>
          </div>

          <div class="px-4 py-3 bg-white flex-shrink-0">
            <v-text-field
              v-model="searchEmployee"
              placeholder="Rechercher un salarié..."
              density="compact"
              variant="outlined"
              hide-details
              prepend-inner-icon="mdi-magnify"
              base-color="grey-lighten-2"
              color="purple"
              bg-color="grey-lighten-5"
              class="rounded-lg"
            ></v-text-field>
          </div>

          <div class="flex-grow-1 overflow-hidden px-2 pb-2">
            <v-data-table
              :headers="employeeHeaders"
              :items="filteredEmployees"
              density="comfortable"
              hover
              fixed-header
              height="60vh"
              class="clean-table"
              items-per-page="-1"
            >
               <template #no-data>
                <div class="py-10 text-center text-grey">Aucun salarié trouvé</div>
              </template>

              <template #item.first_name="{ item }">
                 <span class="font-weight-medium text-grey-darken-3">{{ item.first_name }}</span>
              </template>

              <template #item.actions="{ item }">
                <v-btn icon variant="text" color="grey-lighten-1" size="small" class="delete-hover" @click="confirmDelete('employee', item.id)">
                  <v-icon size="20">mdi-trash-can-outline</v-icon>
                </v-btn>
              </template>
              <template #bottom></template>
            </v-data-table>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-card class="flex-shrink-0 mt-4 rounded-xl px-4 py-3 mx-auto elevation-4 d-flex align-center justify-space-between bg-teal-darken-3" style="width: 100%; min-height: 80px;">
        
        <div class="d-flex align-center mr-6 hidden-sm-and-down">
            <div class="bg-white rounded-circle pa-2 mr-3 d-flex shadow-sm">
                <v-icon color="teal-darken-3" size="20">mdi-link-variant</v-icon>
            </div>
            <div>
                <div class="font-weight-bold text-body-2 text-white">Créer un binôme</div>
                <div class="text-caption text-teal-lighten-4">Associer client & salarié</div>
            </div>
        </div>

        <div class="d-flex flex-grow-1 align-center gap-3">
             <v-autocomplete
                v-model="selectedClient"
                :items="availableClients"
                item-title="full_name"
                item-value="id"
                label="Sélectionner un client"
                variant="solo"
                density="compact"
                hide-details
                bg-color="white"
                class="rounded-lg flex-grow-1"
                flat
                menu-icon="mdi-chevron-down"
            >
                <template #prepend-inner><v-icon size="20" color="grey-lighten-1" class="mr-1">mdi-account</v-icon></template>
            </v-autocomplete>

            <v-icon icon="mdi-arrow-right" color="white" class="hidden-xs opacity-80"></v-icon>

            <v-autocomplete
                v-model="selectedEmployee"
                :items="employees"
                item-title="full_name"
                item-value="id"
                label="Sélectionner un salarié"
                variant="solo"
                density="compact"
                hide-details
                bg-color="white"
                class="rounded-lg flex-grow-1"
                flat
                menu-icon="mdi-chevron-down"
            >
                <template #prepend-inner><v-icon size="20" color="grey-lighten-1" class="mr-1">mdi-briefcase</v-icon></template>
            </v-autocomplete>

            <v-btn
                color="white"
                class="text-teal-darken-4 font-weight-bold px-4 ml-1 rounded-lg text-capitalize"
                height="44"
                :disabled="!selectedClient || !selectedEmployee"
                @click="goToCreateBinome"
                elevation="2"
            >
                Associer
                <v-icon end>mdi-check</v-icon>
            </v-btn>
        </div>
    </v-card>

    <v-dialog v-model="dialogVisible" max-width="400px">
      <v-card class="rounded-xl pa-5">
        <h3 class="text-h6 font-weight-bold mb-4">
           {{ dialogType === 'client' ? 'Nouveau Client' : 'Nouveau Salarié' }}
        </h3>
        <v-text-field v-model="firstName" label="Prénom" variant="outlined" density="comfortable" class="mb-3" rounded="lg"></v-text-field>
        <v-text-field v-model="lastName" label="Nom" variant="outlined" density="comfortable" rounded="lg"></v-text-field>
        <v-card-actions class="justify-end mt-4 pa-0">
           <v-btn variant="text" rounded="lg" color="grey" @click="closeDialog">Annuler</v-btn>
           <v-btn color="primary" variant="flat" rounded="lg" class="px-4" @click="createEntry">Créer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirmVisible" max-width="350px">
       <v-card class="rounded-xl pa-6 text-center">
         <v-icon color="red-lighten-4" size="56" class="mb-4">mdi-alert-circle</v-icon>
         <div class="text-h6 font-weight-bold mb-2">Confirmer la suppression ?</div>
         <p class="text-body-2 text-grey mb-6">Cette action est irréversible.</p>
         <div class="d-flex justify-center gap-3">
            <v-btn variant="outlined" color="grey" rounded="lg" class="px-6" @click="confirmVisible = false">Non</v-btn>
            <v-btn color="red" variant="flat" rounded="lg" class="px-6" @click="deleteConfirmed">Oui</v-btn>
         </div>
       </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import api from "@/services/api";

const router = useRouter();

// --- STATE ---
const clients = ref([]);
const availableClients = ref([]);
const employees = ref([]);
const loading = ref(false);

const searchClient = ref("");
const searchEmployee = ref("");

const dialogVisible = ref(false);
const dialogType = ref(null);
const firstName = ref("");
const lastName = ref("");

const selectedClient = ref(null);
const selectedEmployee = ref(null);

const confirmVisible = ref(false);
const deleteTarget = ref({ type: null, id: null });

// --- HEADERS (Simplifiés pour le design) ---
const clientHeaders = [
  { title: "Prénom", key: "first_name", align: 'start' },
  { title: "Nom", key: "last_name", align: 'start' },
  { title: "", key: "actions", sortable: false, align: 'end', width: "50px" },
];
const employeeHeaders = [
  { title: "Prénom", key: "first_name", align: 'start' },
  { title: "Nom", key: "last_name", align: 'start' },
  { title: "", key: "actions", sortable: false, align: 'end', width: "50px" },
];

// --- COMPUTED ---
const filteredClients = computed(() => {
  const s = searchClient.value.toLowerCase();
  return clients.value.filter(c => 
    c.first_name.toLowerCase().includes(s) || c.last_name.toLowerCase().includes(s)
  );
});

const filteredEmployees = computed(() => {
  const s = searchEmployee.value.toLowerCase();
  return employees.value.filter(e => 
    e.first_name.toLowerCase().includes(s) || e.last_name.toLowerCase().includes(s)
  );
});

// --- ACTIONS ---
function openDialog(type) {
  dialogType.value = type;
  dialogVisible.value = true;
}
function closeDialog() {
  dialogVisible.value = false;
  firstName.value = "";
  lastName.value = "";
}

function confirmDelete(type, id) {
  deleteTarget.value = { type, id };
  confirmVisible.value = true;
}

async function deleteConfirmed() {
  const { type, id } = deleteTarget.value;
  confirmVisible.value = false;
  try {
      if (type === "client") await api.delete(`/clients/${id}/`);
      if (type === "employee") await api.delete(`/employees/${id}/`);
      await fetchData();
  } catch(e) { console.error(e); }
}

async function createEntry() {
  const endpoint = dialogType.value === "client" ? "/clients/" : "/employees/";
  try {
      await api.post(endpoint, { first_name: firstName.value, last_name: lastName.value });
      closeDialog();
      await fetchData();
  } catch(e) { console.error(e); }
}

function goToCreateBinome() {
  if (!selectedClient.value || !selectedEmployee.value) return;
  router.push({
    path: "/creation-binome",
    query: { client_id: selectedClient.value, employee_id: selectedEmployee.value },
  });
}

// --- INIT ---
onMounted(fetchData);
async function fetchData() {
  loading.value = true;
  try {
    const [cRes, aRes, eRes] = await Promise.all([
      api.get("/clients/"),
      api.get("/clients/disponibles/"),
      api.get("/employees/"),
    ]);
    
    clients.value = cRes.data.map(c => ({ ...c, full_name: `${c.first_name} ${c.last_name}` }));
    availableClients.value = aRes.data.map(c => ({ ...c, full_name: `${c.first_name} ${c.last_name}` }));
    employees.value = eRes.data.map(e => ({ ...e, full_name: `${e.first_name} ${e.last_name}` }));
  } catch(e) { console.error(e); }
  finally { loading.value = false; }
}
</script>

<style scoped>
/* Force la hauteur sans scroll sur le body */
.h-screen { height: 100vh; }

/* Bordures subtiles */
.border-thin { border: 1px solid rgba(0, 0, 0, 0.06) !important; }

/* Styles du tableau pour le rendre "Clean" */
.clean-table :deep(th) {
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.clean-table :deep(td) {
  border-bottom: 1px solid #f8f9fa !important;
  height: 56px !important; 
}

/* Scrollbar personnalisée fine */
.clean-table :deep(.v-table__wrapper) { scrollbar-width: thin; }
.clean-table :deep(.v-table__wrapper)::-webkit-scrollbar { width: 6px; }
.clean-table :deep(.v-table__wrapper)::-webkit-scrollbar-track { background: transparent; }
.clean-table :deep(.v-table__wrapper)::-webkit-scrollbar-thumb { background: #e0e0e0; border-radius: 4px; }
.clean-table :deep(.v-table__wrapper)::-webkit-scrollbar-thumb:hover { background: #bdbdbd; }

/* Bouton suppression */
.delete-hover { opacity: 0.6; transition: all 0.2s; }
.delete-hover:hover { opacity: 1; color: #ef5350 !important; background-color: #ffebee; }

.gap-3 { gap: 12px; }
</style>