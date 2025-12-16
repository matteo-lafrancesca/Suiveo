<template>
  <v-dialog v-model="dialog" max-width="500px">
    <v-card class="rounded-xl">
      <v-card-title class="px-6 pt-6 pb-0 text-h6 font-weight-bold">
        Programmer un appel manuel
      </v-card-title>
      
      <v-card-text class="px-6 py-4">
        <v-alert 
          type="info" 
          variant="tonal" 
          density="compact" 
          class="mb-4 text-caption border-thin"
        >
          Cet appel s'ajoutera au planning sans perturber le cycle automatique des appels récurrents.
        </v-alert>

        <div v-if="loadingTemplates" class="d-flex justify-center my-4">
          <v-progress-circular indeterminate size="24" color="primary" />
        </div>

        <template v-else>
          <v-select
            v-model="form.template_id"
            :items="templates"
            item-title="name"
            item-value="id"
            label="Type d'appel (Template)"
            variant="outlined"
            density="comfortable"
            color="primary"
            class="mb-2"
            :rules="[v => !!v || 'Requis']"
          ></v-select>

          <DatePickerField
            v-model="form.date"
            label="Date prévue"
            class="mb-2"
            :min="minDate"
            :rules="[
              v => !!v || 'Requis',
              v => v >= minDate || 'La date ne peut pas être dans le passé'
            ]"
          />

          <v-text-field
            v-model="form.title"
            label="Titre personnalisé (Facultatif)"
            placeholder="Ex: Point urgent situation..."
            variant="outlined"
            density="comfortable"
            color="primary"
            hint="Si vide, prendra le nom du template"
            persistent-hint
          ></v-text-field>
        </template>
      </v-card-text>

      <v-card-actions class="px-6 pb-6 pt-0 justify-end">
        <v-btn variant="text" @click="dialog = false">Annuler</v-btn>
        
        <v-btn 
          color="primary" 
          variant="flat" 
          rounded="lg"
          :loading="submitting"
          :disabled="!form.template_id || !form.date || form.date < minDate"
          @click="submit"
        >
          Programmer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue';
import api from "@/services/api";
import DatePickerField from "@/components/DatePickerField.vue";

const props = defineProps({
  modelValue: Boolean,
  binomeId: { type: [Number, String], required: true }
});

const emit = defineEmits(['update:modelValue', 'success']);

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});

// Calcul de la date minimum (Aujourd'hui au format YYYY-MM-DD)
const minDate = new Date().toISOString().split('T')[0];

const templates = ref([]);
const loadingTemplates = ref(false);
const submitting = ref(false);

const form = reactive({
  template_id: null,
  date: minDate, // On initialise directement à aujourd'hui
  title: ""
});

watch(dialog, async (val) => {
  if (val) {
    // Reset de la date à l'ouverture pour éviter de garder une vieille date si on réouvre
    form.date = new Date().toISOString().split('T')[0];
    
    if (templates.value.length === 0) {
      loadingTemplates.value = true;
      try {
        const { data } = await api.get('/binomes/manual-templates/');
        templates.value = data;
      } catch (e) {
        console.error("Erreur chargement templates", e);
      } finally {
        loadingTemplates.value = false;
      }
    }
  }
});

async function submit() {
  // Double vérification avant envoi
  if (!form.template_id || !form.date || form.date < minDate) return;
  
  submitting.value = true;
  try {
    await api.post(`/binomes/${props.binomeId}/schedule-manual/`, {
      template_id: form.template_id,
      date: form.date,
      title: form.title
    });
    
    emit('success');
    dialog.value = false;
    
    form.template_id = null;
    form.title = "";
  } catch (e) {
    console.error("Erreur création appel", e);
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.border-thin { border: 1px solid rgba(0,0,0,0.12) !important; }
</style>