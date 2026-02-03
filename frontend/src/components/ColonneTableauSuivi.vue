<template>
  <v-sheet
    class="d-flex flex-column rounded-lg elevation-0 border h-100 w-100"
    color="grey-lighten-5"
  >
    <div 
      class="pa-4 flex-shrink-0 d-flex align-center justify-space-between rounded-t-lg bg-white border-b"
      :style="`border-top: 4px solid ${getColorCode(color)};`"
    >
      <div class="d-flex align-center">
        <v-icon :color="color" class="mr-2">{{ icon }}</v-icon>
        <span class="text-h6 font-weight-bold text-grey-darken-3">{{ titre }}</span>
      </div>
      <v-chip size="small" variant="tonal" :color="color" class="font-weight-bold">
        {{ items.length }}
      </v-chip>
    </div>

    <div class="flex-grow-1 pa-3 custom-scrollbar" style="overflow-y: auto; min-height: 0;">
      
      <template v-if="items.length">
        <div v-for="b in items" :key="b.id" class="mb-3">
           <BinomeCard
             :binome="b"
             :nextCallType="b.next_call?.template.type"
             class="elevation-1 border-sm" 
           />
        </div>
      </template>

      <div v-else class="d-flex flex-column align-center justify-center h-100 opacity-50">
        <v-icon size="40" color="grey-lighten-1" class="mb-2">mdi-inbox-outline</v-icon>
        <span class="text-caption text-grey">Aucune donnée</span>
      </div>

    </div>
  </v-sheet>
</template>

<script setup>
import BinomeCard from "@/components/BinomeCard.vue";
import { useTheme } from 'vuetify'

const props = defineProps({
  titre: String,
  icon: String,
  color: String, 
  items: {
    type: Array,
    required: true,
  },
});

const theme = useTheme()

const getColorCode = (colorName) => {
    return theme.current.value.colors[colorName] || colorName;
}
</script>

<style scoped>
/* Scrollbar fine et moderne */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.15);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.3);
}
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.15) transparent;
}
</style>