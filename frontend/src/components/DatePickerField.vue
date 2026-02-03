<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    location="bottom start"
  >
    <template v-slot:activator="{ props }">
      <v-text-field
        v-bind="props"
        :model-value="formattedDate"
        :label="label"
        variant="outlined"
        density="comfortable"
        color="primary"
        readonly
        append-inner-icon="mdi-calendar"
        :error-messages="errorMessages"
        :min="min"
        :rules="rules"
        :class="customClass"
        :hide-details="hideDetails"
      ></v-text-field>
    </template>
    <v-date-picker
      v-model="pickerDate"
      :min="min"
      :allowed-dates="allowedDates"
      @update:model-value="onDateSelected"
      color="primary"
      locale="fr"
    ></v-date-picker>
  </v-menu>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  modelValue: String, // YYYY-MM-DD
  label: String,
  min: String,
  allowedDates: Function,
  errorMessages: [String, Array],
  rules: Array,
  customClass: String,
  hideDetails: [Boolean, String]
});

const emit = defineEmits(['update:modelValue']);

const menu = ref(false);
const pickerDate = ref(null);

watch(() => props.modelValue, (val) => {
  if (val) {
    pickerDate.value = new Date(val);
  } else {
    pickerDate.value = null;
  }
}, { immediate: true });

const formattedDate = computed(() => {
  if (!props.modelValue) return "";
  return new Date(props.modelValue).toLocaleDateString("fr-FR");
});

function onDateSelected(date) {
  if (!date) return;
  
  // Utilisation des composants locaux pour éviter les problèmes de fuseau horaire
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const dateString = `${year}-${month}-${day}`;
  
  emit('update:modelValue', dateString);
  menu.value = false;
}
</script>
