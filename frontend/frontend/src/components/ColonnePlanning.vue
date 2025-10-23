<template>
  <v-col
    cols="12"
    md="2"
    class="d-flex flex-column pa-3 colonne-planning"
  >
    <v-sheet
      color="background"
      class="d-flex flex-column rounded-xl elevation-3 pa-4"
      style="height: 73vh;"
    >
      <!-- Titre -->
      <div class="d-flex justify-center align-center mb-4">
        <span class="text-h6 font-weight-bold text-primary text-center">
          {{ titre }}
        </span>
      </div>

      <!-- Liste des binômes -->
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
            max-width="460"
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
  date: String,
  items: {
    type: Array,
    required: true,
  },
});
</script>

<style scoped>
/* ✅ élargit légèrement chaque colonne */
.colonne-planning {
  flex: 1 1 22%;
  max-width: 20%;
}

/* Meilleure respiration entre les colonnes */
.v-row {
  gap: 12px;
}

/* Ajustement du titre */
.text-h6 {
  font-size: 1.15rem;
  font-weight: 700;
}

/* Style du texte d’état vide */
.text-secondary {
  color: #64748b;
}
</style>
