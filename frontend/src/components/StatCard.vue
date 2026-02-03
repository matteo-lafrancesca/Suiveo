<template>
  <v-card
    class="rounded-xl border-thin"
    elevation="0"
    :color="color"
    variant="tonal"
  >
    <v-card-text class="d-flex align-center pa-4">
      <v-avatar
        :color="color"
        variant="elevated"
        size="48"
        class="mr-4 rounded-lg elevation-2"
      >
        <v-icon color="white" size="24">{{ icon }}</v-icon>
      </v-avatar>
      
      <div>
        <div class="text-caption font-weight-bold text-uppercase opacity-70 mb-1">
          {{ title }}
        </div>
        <div class="text-h4 font-weight-bold">
          {{ value }}
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
defineProps({
  title: String,
  value: [Number, String],
  icon: String,
  color: {
    type: String,
    default: "primary"
  }
});
</script>
