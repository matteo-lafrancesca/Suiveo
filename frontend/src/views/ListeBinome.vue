<template>
  <v-container fluid class="h-screen-offset bg-grey-lighten-4 pa-6 overflow-hidden">
    <v-card class="elevation-0 rounded-lg border h-100 d-flex flex-column">
      
      <div class="px-6 py-4 d-flex align-center justify-space-between border-b bg-white flex-shrink-0">
        <div class="d-flex align-center">
            <v-avatar color="primary" variant="tonal" size="40" class="mr-3 rounded-lg">
                <v-icon color="primary">mdi-format-list-bulleted</v-icon>
            </v-avatar>
            <div>
                <h2 class="text-h6 font-weight-bold text-grey-darken-3 mb-0">Gestion des Binômes</h2>
                <span class="text-caption text-grey-darken-1">{{ filteredBinomes.length }} dossiers actifs</span>
            </div>
        </div>

        <div class="d-flex align-center" style="gap: 12px; width: 400px;">
          <v-text-field
            v-model="searchQuery"
            placeholder="Rechercher..."
            density="compact"
            hide-details
            variant="outlined"
            prepend-inner-icon="mdi-magnify"
            class="bg-white rounded-lg"
            clearable
          />
           <v-btn icon="mdi-refresh" variant="text" color="grey-darken-1" :loading="loading" @click="fetchBinomes"></v-btn>
        </div>
      </div>

      <v-data-table
        :headers="headers"
        :items="filteredBinomes"
        :loading="loading"
        :items-per-page="-1"
        hide-default-footer
        fixed-header
        hover
        density="default"
        class="flex-grow-1"
        style="height: 100%; overflow-y: auto;" 
      >
        <template v-slot:headers="{ columns, isSorted, getSortIcon, toggleSort }">
            <tr class="bg-grey-lighten-5">
                <template v-for="column in columns" :key="column.key">
                    <th 
                        class="text-caption font-weight-bold text-uppercase text-grey-darken-1 border-b py-3"
                        :style="{ width: column.width, cursor: column.sortable ? 'pointer' : 'default' }"
                        @click="() => column.sortable && toggleSort(column)"
                    >
                        <div class="d-flex align-center" :class="column.align === 'end' ? 'justify-end' : (column.align === 'center' ? 'justify-center' : '')">
                            {{ column.title }}
                            <v-icon v-if="isSorted(column)" :icon="getSortIcon(column)" size="small" class="ml-1"></v-icon>
                        </div>
                    </th>
                </template>
            </tr>
        </template>

        <template #item.client_name="{ item }">
            <div class="d-flex align-center py-2">
                <v-avatar color="blue-lighten-5" rounded="lg" size="36" class="mr-3 text-blue-darken-3 font-weight-bold text-caption">
                    {{ item.client_initials }}
                </v-avatar>
                <div class="d-flex flex-column">
                    <span class="font-weight-bold text-body-2 text-grey-darken-3">
                        {{ item.client_name || 'Client Inconnu' }}
                    </span>
                    <span class="text-caption text-grey">Client</span>
                </div>
            </div>
        </template>

        <template #item.employee_name="{ item }">
             <div class="d-flex align-center py-2">
                <v-avatar color="purple-lighten-5" rounded="lg" size="36" class="mr-3 text-purple-darken-3 font-weight-bold text-caption">
                    {{ item.employee_initials }}
                </v-avatar>
                <div class="d-flex flex-column">
                    <span class="font-weight-medium text-body-2 text-grey-darken-3">
                        {{ item.employee_name || 'Non assigné' }}
                    </span>
                    <span class="text-caption text-grey">Intervenant</span>
                </div>
            </div>
        </template>

        <template #item.rhythm_display="{ item }">
             <v-chip 
                v-if="item.rhythm_display"
                size="small" variant="tonal" color="info" class="font-weight-medium" label
             >
                <v-icon start size="14">mdi-clock-time-four-outline</v-icon>
                {{ item.rhythm_display }}
             </v-chip>
             <span v-else class="text-caption text-grey">—</span>
        </template>

        <template #item.state="{ item }">
          <div class="d-flex align-center" v-if="item.state">
              <v-icon :color="getStateColor(item.state)" size="10" class="mr-2">mdi-circle</v-icon>
              <span class="text-body-2" :class="`text-${getStateColor(item.state)}`">
                  {{ item.state }}
              </span>
          </div>
          <span v-else class="text-caption text-grey">Indéfini</span>
        </template>

        <template #item.week_sort_key="{ item }">
            <div v-if="item.next_call && item.next_call.week_number" class="d-flex flex-column align-center justify-center">
                 <v-sheet 
                    color="grey-lighten-4" rounded 
                    class="d-flex align-center justify-center font-weight-bold text-grey-darken-3"
                    height="28" width="40"
                 >
                    {{ item.next_call.week_number }}
                 </v-sheet>
                 <span class="text-caption text-grey-lighten-2 mt-1" style="font-size: 0.65rem;">
                    {{ item.next_call.year }}
                 </span>
            </div>
             <span v-else class="text-caption text-grey-lighten-1 d-block text-center">—</span>
        </template>

        <template #item.actions="{ item }">
            <div class="d-flex justify-end">
                <v-btn icon="mdi-arrow-right" variant="text" density="comfortable" color="grey-lighten-1" class="action-btn" @click="goToBinome(item.id)"></v-btn>
            </div>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import api from "@/services/api";
import { useRouter } from "vue-router";
import { getStateColor } from "@/helpers/binomeHelpers";

const router = useRouter();
const binomes = ref([]);
const loading = ref(false);
const searchQuery = ref("");

const headers = [
  { title: "Client", key: "client_name", sortable: true, width: '22%' },
  { title: "Intervenant", key: "employee_name", sortable: true, width: '22%' },
  { title: "Rythme", key: "rhythm_display", sortable: true, width: '14%' },
  { title: "Statut", key: "state", sortable: true, width: '14%' },
  { title: "Prochaine Action", key: "next_call.template_name", sortable: false, width: '18%' },
  { title: "Sem.", key: "week_sort_key", sortable: true, align: 'center', width: '6%' },
  { title: "", key: "actions", sortable: false, align: 'end', width: '4%' },
];

onMounted(fetchBinomes);

async function fetchBinomes() {
  loading.value = true;
  try {
    const { data } = await api.get("/binomes/enrichis/"); 
    // Si votre URL est "/binomes/" dans l'api, changez ci-dessus
    // Assurez-vous que le backend renvoie bien les nouveaux champs
    binomes.value = data; 
  } finally {
    loading.value = false;
  }
}

const filteredBinomes = computed(() => {
  const query = searchQuery.value.toLowerCase().trim();
  if (!query) return binomes.value;

  return binomes.value.filter((b) => {
    // Sécurisation : on vérifie que les champs existent avant de faire toLowerCase()
    const cName = b.client_name ? b.client_name.toLowerCase() : '';
    const eName = b.employee_name ? b.employee_name.toLowerCase() : '';
    const state = b.state ? b.state.toLowerCase() : '';
    const rhythm = b.rhythm_display ? b.rhythm_display.toLowerCase() : '';
    const week = (b.next_call && b.next_call.week_number) ? b.next_call.week_number.toString() : '';

    return (
      cName.includes(query) ||
      eName.includes(query) ||
      state.includes(query) ||
      rhythm.includes(query) ||
      week.includes(query)
    );
  });
});

function goToBinome(id) {
  router.push(`/binome/${id}`);
}
</script>

<style scoped>
.h-screen-offset { height: calc(100vh - 64px); }
.action-btn:hover { color: rgb(var(--v-theme-primary)) !important; background-color: rgb(var(--v-theme-primary), 0.1); }
:deep(.v-data-table__tr:hover td) { background-color: #FAFAFA !important; }
</style>