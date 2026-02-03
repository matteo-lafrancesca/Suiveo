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
            <DatePickerField
              v-model="form.start_date"
              label="Date de début"
              :min="minDate"
              :allowed-dates="isDateAllowed"
              :error-messages="dateError"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model.number="form.weeks_count"
              type="number"
              label="Durée (semaines)"
              variant="outlined"
              density="comfortable"
              color="primary"
              min="1"
            ></v-text-field>
          </v-col>
        </v-row>

        <div class="text-center mt-2 text-body-2 text-medium-emphasis">
            Fin de la pause : <strong>{{ endDateDisplay }}</strong>
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
import DatePickerField from "@/components/DatePickerField.vue";

const props = defineProps({
  modelValue: Boolean,
  binomeId: { type: [Number, String], required: true },
  firstInterventionDate: { type: String, default: "" }
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
  weeks_count: 1
});

const days = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];

const allowedDayIndex = computed(() => {
    if (!props.firstInterventionDate) return -1;
    const parts = props.firstInterventionDate.split('-');
    const date = new Date(parts[0], parts[1] - 1, parts[2]);
    return date.getDay();
});

function isDateAllowed(val) {
    const date = new Date(val);
    return date.getDay() === allowedDayIndex.value;
}

const allowedDayName = computed(() => {
    if (allowedDayIndex.value === -1) return "jour défini";
    return days[allowedDayIndex.value];
});

const isDateValid = computed(() => {
    if (!form.start_date) return false;
    const date = new Date(form.start_date);
    return date.getDay() === allowedDayIndex.value;
});

const dateError = computed(() => {
    if (form.start_date && !isDateValid.value) {
        return [`Doit être un ${allowedDayName.value}`];
    }
    return [];
});

const endDate = computed(() => {
    if (!form.start_date) return null;
    const start = new Date(form.start_date);
    const end = new Date(start);
    end.setDate(start.getDate() + (form.weeks_count * 7));
    return end;
});

const endDateDisplay = computed(() => {
    if (!endDate.value) return "—";
    return endDate.value.toLocaleDateString("fr-FR");
});

const durationDisplay = computed(() => {
    if (!form.weeks_count) return "—";
    return `${form.weeks_count} semaine${form.weeks_count > 1 ? 's' : ''}`;
});

const isValid = computed(() => {
  return form.start_date && isDateValid.value && form.weeks_count > 0;
});

async function submit() {
  if (!isValid.value) return;
  
  submitting.value = true;
  try {
    const end = endDate.value.toISOString().split('T')[0];

    await api.post(`/binomes/${props.binomeId}/schedule-pause/`, {
      start_date: form.start_date,
      end_date: end
    });
    
    emit('success');
    dialog.value = false;
    // Reset form
    form.weeks_count = 1; 
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