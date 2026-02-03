<template>
  <div class="d-flex flex-column h-100" style="flex: 1; min-width: 240px; max-width: 100%;">
    
    <v-sheet
      class="d-flex flex-column rounded-lg elevation-0 border h-100 w-100"
      :class="isToday ? 'bg-blue-lighten-5' : 'bg-grey-lighten-5'"
      :style="isToday ? 'border-color: rgba(var(--v-theme-primary), 0.5) !important;' : ''"
    >
      <div 
        class="pa-3 flex-shrink-0 d-flex align-center justify-space-between rounded-t-lg bg-white border-b"
        :style="`border-top: 4px solid ${isToday ? 'rgb(var(--v-theme-primary))' : '#E0E0E0'};`"
      >
        <div class="d-flex flex-column">
          <span class="text-subtitle-2 font-weight-bold text-uppercase text-grey-darken-2">
            {{ dayName }}
          </span>
          <span class="text-h6 font-weight-bold text-grey-darken-3" style="line-height: 1;">
            {{ formattedDate }}
          </span>
        </div>
        
        <v-chip 
           v-if="items.length > 0"
            size="small" 
            variant="tonal" 
            :color="isToday ? 'primary' : 'grey'" 
            class="font-weight-bold"
        >
          {{ items.length }}
        </v-chip>
      </div>

      <div class="flex-grow-1 pa-2 custom-scrollbar" style="overflow-y: auto; min-height: 0;">
        <template v-if="items.length">
          <div v-for="b in items" :key="b.id" class="mb-3">
             <BinomeCard
               :binome="b"
               :nextCallType="b.next_call?.template_type"
               class="elevation-1 border-sm" 
             />
          </div>
        </template>
        </div>
    </v-sheet>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import BinomeCard from "@/components/BinomeCard.vue";

const props = defineProps({
  titre: String,
  date: String,
  items: {
    type: Array,
    required: true,
  },
});

const dayName = computed(() => {
    if(!props.date) return props.titre;
    const d = new Date(props.date);
    return d.toLocaleDateString('fr-FR', { weekday: 'long' });
});

const formattedDate = computed(() => {
    if(!props.date) return '';
    const d = new Date(props.date);
    return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
});

const isToday = computed(() => {
    if(!props.date) return false;
    const today = new Date();
    const colDate = new Date(props.date);
    return today.toDateString() === colDate.toDateString();
});
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.25);
}
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.1) transparent;
}
</style>