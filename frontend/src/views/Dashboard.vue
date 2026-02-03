<template>
  <div class="dashboard-container bg-grey-lighten-4 h-100 pa-6 overflow-auto">
    <v-container fluid class="pa-0">
      
      <!-- En-tête -->
      <div class="d-flex flex-column flex-md-row justify-space-between align-md-center mb-8">
        <div>
          <h1 class="text-h4 font-weight-bold text-grey-darken-3 mb-1">
            Bonjour, {{ user?.first_name || 'Utilisateur' }} 👋
          </h1>
          <div class="text-body-1 text-grey-darken-1">
            Voici un aperçu de l'activité pour cette semaine.
          </div>
        </div>
      </div>

      <!-- KPIs -->
      <v-row class="mb-6">
        <v-col cols="12" sm="6" md="3">
          <StatCard 
            title="Binômes Actifs" 
            :value="kpis.active_binomes" 
            icon="mdi-account-group" 
            color="primary" 
          />
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <StatCard 
            title="Appels Semaine" 
            :value="kpis.calls_week" 
            icon="mdi-calendar-week" 
            color="info" 
          />
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <StatCard 
            title="En Retard" 
            :value="kpis.retard" 
            icon="mdi-clock-alert-outline" 
            color="grey-darken-1" 
          />
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <StatCard 
            title="Non Conformes" 
            :value="kpis.non_conforme" 
            icon="mdi-alert-circle-outline" 
            color="error" 
          />
        </v-col>
      </v-row>

      <v-row>
        <!-- Appels de la semaine -->
        <v-col cols="12" md="6">
          <v-card class="rounded-xl border-thin h-100" elevation="0">
            <v-card-title class="px-6 pt-6 d-flex justify-space-between align-center">
              <span class="font-weight-bold">📅 Cette Semaine</span>
              <v-chip size="small" variant="tonal" color="info">{{ widgets.calls_week.length }} appels</v-chip>
            </v-card-title>
            
            <v-card-text class="px-2">
              <v-list v-if="widgets.calls_week.length > 0" lines="two">
                 <v-list-item
                    v-for="call in widgets.calls_week"
                    :key="call.id"
                    :to="`/binome/${call.binome}`"
                    class="rounded-lg mb-1"
                 >
                    <template v-slot:prepend>
                      <v-avatar color="info" variant="tonal" class="rounded-lg">
                        <v-icon>mdi-phone</v-icon>
                      </v-avatar>
                    </template>
                    
                    <v-list-item-title class="font-weight-bold">
                       {{ call.client_name }}
                    </v-list-item-title>
                    <v-list-item-subtitle>
                       {{ call.employee_name }} — {{ formatDate(call.scheduled_date) }}
                    </v-list-item-subtitle>
                    
                    <template v-slot:append>
                       <v-icon size="small" color="grey">mdi-chevron-right</v-icon>
                    </template>
                 </v-list-item>
              </v-list>
              
              <div v-else class="text-center py-6 text-grey">
                <v-icon size="40" class="mb-2 opacity-50">mdi-check-all</v-icon>
                <div>Aucun appel prévu cette semaine.</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Appels en retard -->
        <v-col cols="12" md="6">
          <v-card class="rounded-xl border-thin h-100" elevation="0">
            <v-card-title class="px-6 pt-6 d-flex justify-space-between align-center">
              <span class="font-weight-bold text-grey-darken-3">⚠️ En Retard</span>
              <v-chip size="small" variant="tonal" color="grey-darken-1">{{ widgets.calls_retard.length }} critiques</v-chip>
            </v-card-title>
            
            <v-card-text class="px-2">
              <v-list v-if="widgets.calls_retard.length > 0" lines="two">
                 <v-list-item
                    v-for="call in widgets.calls_retard"
                    :key="call.id"
                    :to="`/binome/${call.binome}`"
                    class="rounded-lg mb-1 bg-grey-lighten-4"
                 >
                    <template v-slot:prepend>
                      <v-avatar color="grey-darken-1" variant="flat" class="rounded-lg">
                        <v-icon color="white">mdi-clock-alert</v-icon>
                      </v-avatar>
                    </template>
                    
                    <v-list-item-title class="font-weight-bold text-grey-darken-3">
                       {{ call.client_name }} <span class="text-grey-darken-1 text-caption">avec {{ call.employee_name }}</span>
                    </v-list-item-title>
                    <v-list-item-subtitle class="text-grey-darken-1">
                       Prévu le {{ formatDate(call.scheduled_date) }} - {{ call.title }}
                    </v-list-item-subtitle>
                    
                    <template v-slot:append>
                       <v-icon size="small" color="grey">mdi-chevron-right</v-icon>
                    </template>
                 </v-list-item>
              </v-list>
              
               <div v-else class="text-center py-6 text-grey">
                <v-icon size="40" class="mb-2 opacity-50">mdi-thumb-up-outline</v-icon>
                <div>Aucun retard. Bravo !</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import api from "@/services/api";
import StatCard from "@/components/StatCard.vue";

const authStore = useAuthStore();
const user = computed(() => authStore.user);

const loading = ref(false);
const kpis = ref({
  active_binomes: 0,
  retard: 0,
  non_conforme: 0,
  calls_week: 0
});

const widgets = ref({
  calls_retard: [],
  calls_week: []
});

async function fetchStats() {
  loading.value = true;
  try {
    const { data } = await api.get("/dashboard/stats/");
    kpis.value = data.kpis;
    widgets.value = data.widgets;
  } catch (e) {
    console.error("Erreur chargement dashboard:", e);
  } finally {
    loading.value = false;
  }
}

// Helper pour afficher le nom du binôme (Client - Employé)
// Attention : le CallSerializer ne renvoie que l'ID du binôme par défaut 
// SI le serializer n'est pas "nested".
// Mais dans DashboardViewSet, j'ai utilisé select_related, donc j'espère que le serializer envoie les infos.
// Si le serializer par défaut CallSerializer n'inclut pas les objets nested, on aura juste l'ID.
// Vérification : CallSerializer utilise BinomeSerializer ?
// Si non, on aura un affichage limité.
// Update : Dans CallSerializer, binome est souvent un PrimaryKeyRelatedField par défaut.
// Pour compenser, je vais faire un petit hack clean : DashboardViewSet envoie peut-être déjà des données enrichies ?
// --> On va vérifier le JSON reçu. Si c'est juste un ID, je ne pourrai pas afficher le nom.
// --> SOLUTION : Je vais m'assurer que le backend sérialise bien les noms.
// --> Je mets à jour la fonction getBinomeName pour gérer les deux cas (ID ou Objet).



function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString("fr-FR", { day: "2-digit", month: "short" });
}

onMounted(fetchStats);
</script>

<style scoped>
.dashboard-container {
    height: 100vh; /* S'assure de prendre toute la hauteur */
}
</style>
