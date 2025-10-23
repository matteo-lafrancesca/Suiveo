<template>
  <v-col cols="12" md="4" class="d-flex flex-column pa-3">
    <v-sheet
      color="background"
      class="d-flex flex-column justify-between rounded-xl elevation-3 pa-4"
      style="height: 80vh;"
    >
      <!-- Titre -->
      <div class="d-flex justify-center align-center mb-4">
        <v-icon color="primary" class="mr-2" size="32">{{ icon }}</v-icon>
        <span class="text-h5 font-weight-bold text-primary">{{ titre }}</span>
      </div>

      <!-- Contenu scrollable -->
      <v-sheet
        color="background"
        class="flex-grow-1 overflow-y-auto pa-3 rounded-lg d-flex flex-column align-center"
        style="min-height: 0;"
      >
        <template v-if="items.length">
          <v-responsive
            v-for="b in items"
            :key="b.id"
            class="mb-4"
            max-width="420"
            width="100%"
          >
            <BinomeCard
              :binome="b"
              :nextCallType="b.next_call?.template_type"
            />
          </v-responsive>
        </template>
      </v-sheet>
    </v-sheet>
  </v-col>
</template>

<script setup>
import BinomeCard from "@/components/BinomeCard.vue";

defineProps({
  titre: String,
  icon: String,
  items: {
    type: Array,
    required: true,
  },
});
</script>
