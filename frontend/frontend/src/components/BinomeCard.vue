<template>
  <v-card class="d-flex align-center mb-3 px-3 py-2" color="grey-lighten-3" rounded="lg">
    <v-avatar size="40" class="me-3" color="blue-lighten-4">
      <v-icon color="blue-darken-2">mdi-account</v-icon>
    </v-avatar>
    <div>
      <span class="text-body-1 font-weight-medium">
        {{ binome.client.last_name }} {{ binome.client.first_name }}
      </span>
      <div class="text-caption text-grey">{{ binome.employee.first_name }} {{ binome.employee.last_name }}</div>
    </div>
  </v-card>
</template>

<script setup>
defineProps({
  binome: {
    type: Object,
    required: true,
  },
});
</script>
