<template>
  <v-dialog v-model="dialog" max-width="500px">
    <v-card class="rounded-xl">
      <v-card-title class="px-6 pt-6 pb-0 text-h6 font-weight-bold">
        Changer d'intervenant
      </v-card-title>
      
      <v-card-text class="px-6 py-4">
        <v-alert type="warning" variant="tonal" density="compact" class="mb-4 text-caption border-thin" icon="mdi-alert">
          Attention : Cette action supprimera le dossier actuel pour en créer un nouveau.
        </v-alert>

        <div v-if="loadingEmployees" class="d-flex justify-center my-4">
          <v-progress-circular indeterminate size="24" color="primary" />
        </div>

        <template v-else>
          <v-autocomplete
            v-model="form.employee_id"
            :items="allEmployees"
            item-title="name"
            item-value="id"
            label="Nouvel Intervenant"
            variant="outlined"
            density="comfortable"
            color="primary"
            class="mb-2"
            :rules="[v => !!v || 'Requis']"
          >
            <template v-slot:item="{ props, item }">
              <v-list-item v-bind="props">
                <template v-slot:append v-if="item.raw.isPrevious">
                  <v-icon color="orange" size="small">mdi-history</v-icon>
                </template>
              </v-list-item>
            </template>
          </v-autocomplete>

          <DatePickerField
            v-model="form.start_date"
            label="Date de début d'intervention"
            class="mb-2"
            :rules="[v => !!v || 'Requis']"
          />

          <v-select
            v-model="form.rhythm"
            :items="rhythmOptions"
            item-title="title"
            item-value="value"
            label="Rythme d'intervention"
            variant="outlined"
            density="comfortable"
            color="primary"
            class="mb-2"
            hide-details="auto"
          ></v-select>

          <v-textarea
            v-model="form.note"
            label="Note (transférée du dossier actuel)"
            variant="outlined"
            density="comfortable"
            color="primary"
            rows="3"
            auto-grow
            class="mb-2"
            hide-details="auto"
          ></v-textarea>

        </template>
      </v-card-text>

      <v-card-actions class="px-6 pb-6 pt-0 justify-end">
        <v-btn variant="text" @click="dialog = false">Annuler</v-btn>
        <v-btn 
          color="blue-grey" 
          variant="flat" 
          rounded="lg"
          :loading="submitting"
          :disabled="!form.employee_id || !form.start_date"
          @click="submit"
        >
          Valider le changement
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from "@/services/api";
import DatePickerField from "@/components/DatePickerField.vue";

const props = defineProps({
  modelValue: Boolean,
  binomeId: { type: [Number, String], required: true },
  clientId: { type: [Number, String], required: true },
  currentRhythm: { type: Number, default: 1 },
  currentNote: { type: String, default: "" } 
});

const emit = defineEmits(['update:modelValue']);
const router = useRouter();

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});

const employees = ref([]);
const previousEmployees = ref([]);
const loadingEmployees = ref(false);
const submitting = ref(false);

const allEmployees = computed(() => {
  // Les employés disponibles ont déjà le format {id, name}
  // Les employés de l'historique viennent du serializer avec {id, first_name, last_name}
  
  const formatEmployee = (e) => ({
    id: e.id,
    name: e.name || `${e.first_name} ${e.last_name}`.trim(),
    isPrevious: false
  });
  
  const formatPrevious = (e) => ({
    id: e.id,
    name: e.name || `${e.first_name} ${e.last_name}`.trim(),
    isPrevious: true
  });
  
  // Marquer les anciens intervenants
  const previousIds = new Set(previousEmployees.value.map(e => e.id));
  
  const previous = previousEmployees.value.map(formatPrevious);
  const others = employees.value
    .filter(e => !previousIds.has(e.id))
    .map(formatEmployee);
  
  return [...previous, ...others];
});

const rhythmOptions = [
  { title: "Hebdomadaire (Standard)", value: 1 },
  { title: "Bimensuel (Toutes les 2 semaines)", value: 2 },
  { title: "Mensuel (Toutes les 4 semaines)", value: 4 },
];

const form = reactive({
  employee_id: null,
  start_date: "",
  rhythm: 1,
  note: "" // 👇 AJOUT
});

watch(dialog, async (val) => {
  if (val) {
    // Reset form
    form.employee_id = null;
    form.start_date = "";
    form.rhythm = props.currentRhythm || 1;
    form.note = props.currentNote || ""; // 👈 Initialisation avec la note actuelle

    loadingEmployees.value = true;
    try {
      // Charger tous les employés disponibles
      const { data: allEmps } = await api.get(`/binomes/${props.binomeId}/available-employees/`);
      employees.value = allEmps || [];
      
      // Charger les anciens intervenants de ce client
      try {
        const { data: prevEmps } = await api.get(`/binomes/previous-employees/?client_id=${props.clientId}`);
        previousEmployees.value = prevEmps || [];
      } catch (e) {
        console.warn("Pas d'historique pour ce client", e);
        previousEmployees.value = [];
      }
    } catch (e) {
      console.error("Erreur chargement employés", e);
    } finally {
      loadingEmployees.value = false;
    }
  }
});

async function submit() {
  if (!form.employee_id || !form.start_date) return;
  
  submitting.value = true;
  try {
    const { data } = await api.post(`/binomes/${props.binomeId}/change-employee/`, {
      employee_id: form.employee_id,
      start_date: form.start_date,
      rhythm: form.rhythm,
      note: form.note // 👈 Envoi de la note
    });
    
    dialog.value = false;
    // Rediriger vers la page Gestion (liste des dossiers)
    router.push({ name: 'Liste Binomes' });

  } catch (e) {
    console.error("Erreur changement intervenant", e);
    if(e.response?.data?.error) {
        alert("Erreur : " + e.response.data.error);
    }
  } finally {
    submitting.value = false;
  }
}
</script>