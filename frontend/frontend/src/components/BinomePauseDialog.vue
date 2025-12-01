<template>
  <v-dialog v-model="dialog" max-width="500px">
    <v-card class="rounded-xl">
      <v-card-title class="px-6 pt-6 pb-0 text-h6 font-weight-bold">
        Programmer une pause
      </v-card-title>
      
      <v-card-text class="px-6 py-4">
        <v-alert 
          type="warning" 
          variant="tonal" 
          density="compact" 
          class="mb-4 text-caption border-thin"
          icon="mdi-clock-alert-outline"
        >
          Cette action décalera automatiquement tous les appels futurs de la durée de la pause ({{ durationDisplay }}).
        </v-alert>

        <v-row dense>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.start_date"
              type="date"
              label="Date de début"
              variant="outlined"
              density="comfortable"
              color="primary"
              :min="minDate"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.end_date"
              type="date"
              label="Date de fin"
              variant="outlined"
              density="comfortable"
              color="primary"
              :min="form.start_date || minDate"
            ></v-text-field>
          </v-col>
        </v-row>

        <div class="text-center mt-2 text-body-2 text-medium-emphasis">
            Durée calculée : <strong>{{ durationDisplay }}</strong>
        </div>
      </v-card-text>

      <v-card-actions class="px-6 pb-6 pt-0 justify-end">
        <v-btn variant="text" @click="dialog = false">Annuler</v-btn>
        <v-btn 
          color="orange-darken-1" 
          variant="flat" 
          rounded="lg"
          :loading="submitting"
          :disabled="!isValid"
          @click="submit"
        >
          Valider la pause
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import api from "@/services/api";

const props = defineProps({
  modelValue: Boolean,
  binomeId: { type: [Number, String], required: true }
});

const emit = defineEmits(['update:modelValue', 'success']);

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});

const minDate = new Date().toISOString().split('T')[0];
const submitting = ref(false);

const form = reactive({
  start_date: minDate,
  end_date: ""
});

// Calcul de la durée en jours pour l'affichage
const durationDisplay = computed(() => {
  if (!form.start_date || !form.end_date) return "—";
  const start = new Date(form.start_date);
  const end = new Date(form.end_date);
  const diffTime = end - start;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays <= 0) return "Erreur de dates";
  return `${diffDays} jour${diffDays > 1 ? 's' : ''}`;
});

const isValid = computed(() => {
  return form.start_date && form.end_date && new Date(form.end_date) > new Date(form.start_date);
});

async function submit() {
  if (!isValid.value) return;
  
  submitting.value = true;
  try {
    await api.post(`/binomes/${props.binomeId}/schedule-pause/`, {
      start_date: form.start_date,
      end_date: form.end_date
    });
    
    emit('success');
    dialog.value = false;
    // Reset form
    form.end_date = ""; 
    form.start_date = minDate;
  } catch (e) {
    console.error("Erreur création pause", e);
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.border-thin { border: 1px solid rgba(0,0,0,0.12) !important; }
</style>