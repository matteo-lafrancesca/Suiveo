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
            :items="employees"
            item-title="name"
            item-value="id"
            label="Nouvel Intervenant"
            variant="outlined"
            density="comfortable"
            color="primary"
            class="mb-2"
            :rules="[v => !!v || 'Requis']"
          ></v-autocomplete>

          <v-text-field
            v-model="form.start_date"
            type="date"
            label="Date de début d'intervention"
            variant="outlined"
            density="comfortable"
            color="primary"
            class="mb-2"
            :rules="[v => !!v || 'Requis']"
          ></v-text-field>

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

const props = defineProps({
  modelValue: Boolean,
  binomeId: { type: [Number, String], required: true },
  currentRhythm: { type: Number, default: 1 },
  // 👇 AJOUT PROP
  currentNote: { type: String, default: "" } 
});

const emit = defineEmits(['update:modelValue']);
const router = useRouter();

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});

const employees = ref([]);
const loadingEmployees = ref(false);
const submitting = ref(false);

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
      const { data } = await api.get(`/binomes/${props.binomeId}/available-employees/`);
      employees.value = data;
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
    router.replace({ name: 'Binome', params: { id: data.new_binome_id } });

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