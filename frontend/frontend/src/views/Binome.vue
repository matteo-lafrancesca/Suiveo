<template>
    <v-container fluid class="pa-8 fill-height content-root">
        <v-row no-gutters class="fill-height d-flex">

            <!-- === Colonne gauche : Fiche Binôme === -->
            <v-col cols="12" md="4" class="pa-3">
                <v-card v-if="binome" class="pa-4 rounded-xl elevation-3" color="surface">
                    <!-- Identité -->
                    <v-row align="center" justify="space-between" class="mb-2">
                        <v-col cols="auto" class="d-flex align-center">
                            <v-avatar size="56" class="mr-3">
                                <v-icon size="32" color="primary">mdi-account</v-icon>
                            </v-avatar>
                            <div>
                                <div class="text-h6 font-weight-medium">
                                    {{ binome.client.first_name }} {{ binome.client.last_name }}
                                </div>
                                <div class="text-body-2 text-secondary">Client</div>
                            </div>
                        </v-col>

                        <v-col cols="auto" class="d-flex justify-end align-center">
                            <v-chip :color="getStateColor(binome.state)"
                                class="px-3 py-1 text-body-2 font-weight-medium chip-opaque" label>
                                <v-icon left size="18" class="mr-1">{{ getStateIcon(binome.state) }}</v-icon>
                                {{ binome.state }}
                            </v-chip>
                        </v-col>
                    </v-row>

                    <v-divider class="my-3"></v-divider>

                    <!-- Informations binôme -->
                    <div class="mb-2">
                        <div class="text-body-2 text-secondary mb-1">Intervenante</div>
                        <div class="text-body-1 font-weight-medium">
                            {{ binome.employee.first_name }} {{ binome.employee.last_name }}
                        </div>
                    </div>

                    <div class="mb-2">
                        <div class="text-body-2 text-secondary mb-1">Première intervention</div>
                        <div class="text-body-1 font-weight-medium">
                            {{ formatDate(binome.first_intervention_date) }}
                        </div>
                    </div>

                    <div>
                        <div class="text-body-2 text-secondary mb-1">Autres informations utiles</div>
                        <div class="text-body-1">{{ binome.note || "—" }}</div>
                    </div>
                </v-card>

                <v-card v-else class="pa-6 d-flex justify-center align-center elevation-2">
                    <v-progress-circular indeterminate color="primary" />
                </v-card>
            </v-col>

            <!-- === Colonne droite : Historique === -->
            <v-col cols="12" md="8" class="pa-3 d-flex flex-column">
                <BinomeTimeline v-if="events.length" :events="events" />
                <div v-else class="text-secondary text-body-2 mt-4">
                    Aucun appel ou visite enregistré pour ce binôme.
                </div>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "@/services/api";
import BinomeTimeline from "@/components/BinomeTimeline.vue";

const route = useRoute();
const binome = ref(null);
const events = ref([]);
const loading = ref(false);

function formatDate(dateStr) {
    if (!dateStr) return "—";
    const d = new Date(dateStr);
    return d.toLocaleDateString("fr-FR", {
        day: "2-digit",
        month: "long",
        year: "numeric",
    });
}

function getStateColor(state) {
    switch (state) {
        case "Conforme": return "success";
        case "Non conforme": return "error";
        case "À appeler": return "warning";
        case "En retard": return "primary";
        default: return "grey";
    }
}

function getStateIcon(state) {
    switch (state) {
        case "Conforme": return "mdi-check-circle";
        case "Non conforme": return "mdi-close-circle";
        case "À appeler": return "mdi-phone";
        case "En retard": return "mdi-alert";
        default: return "mdi-help-circle";
    }
}

async function fetchBinome() {
    loading.value = true;
    try {
        const id = route.params.id;
        const { data } = await api.get(`/binomes/${id}/`);
        binome.value = data;
    } catch (e) {
        console.error("Erreur chargement binôme", e);
    } finally {
        loading.value = false;
    }
}

async function fetchEvents() {
    try {
        const id = route.params.id;
        const [callsRes, visitsRes] = await Promise.all([
            api.get(`/calls/?binome=${id}`),
            api.get(`/field-visits/?binome=${id}`),
        ]);

        const calls = callsRes.data.map((c) => ({ ...c, type: "call" }));
        const visits = visitsRes.data.map((v) => ({ ...v, type: "field_visit" }));

        events.value = [...calls, ...visits].sort((a, b) => {
            const da = new Date(a.actual_date || a.scheduled_date);
            const db = new Date(b.actual_date || b.scheduled_date);
            return da - db;
        });
    } catch (e) {
        console.error("Erreur chargement événements", e);
    }
}

onMounted(async () => {
    await fetchBinome();
    await fetchEvents();
});
</script>

<style scoped>
.v-card {
    border-radius: 20px;
}

.text-secondary {
    color: #6b7280;
}

.chip-opaque {
    background-color: #fde68a !important;
    /* jaune opaque pour "À appeler" */
    color: #000 !important;
}
</style>
