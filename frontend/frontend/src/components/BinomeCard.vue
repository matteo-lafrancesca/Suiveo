<template>
  <v-card
    class="binome-card mx-auto d-flex align-center pa-3 mb-2"
    elevation="0"
    rounded="lg"
    @click="goToBinome"
    :style="cardStyle"
  >
    <v-avatar
      :color="colorTheme"
      variant="flat" 
      rounded="lg"
      size="44"
      class="mr-4 flex-shrink-0 elevation-1"
    >
      <v-icon color="white" size="24">{{ icon }}</v-icon>
    </v-avatar>

    <div class="d-flex flex-column flex-grow-1 overflow-hidden">
      <div class="text-body-2 font-weight-bold text-grey-darken-3 text-truncate">
        {{ displayedName }}
      </div>

      <div class="text-caption text-grey-darken-1 text-truncate mt-1">
        {{ subtitle }}
      </div>
    </div>

    <v-icon 
      icon="mdi-chevron-right" 
      size="22" 
      color="grey-lighten-2" 
      class="chevron-icon"
    ></v-icon>

  </v-card>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useTheme } from 'vuetify';

const router = useRouter();
const theme = useTheme();

const props = defineProps({
  binome: { type: Object, required: true },
  nextCallType: { type: String, required: false }, 
});

// --- Navigation ---

const goToBinome = () => {
  if (props.binome?.id) {
    router.push(`/binome/${props.binome.id}`);
  }
};

// --- Configuration ---

const colorTheme = computed(() => {
  switch (props.nextCallType) {
    case "Client": return "blue-darken-1";    
    case "Employé": return "deep-purple-darken-1"; 
    case "RDV": return "orange-darken-2";     
    case "Visite": return "teal-darken-1";    
    default: return "blue-grey";
  }
});

const icon = computed(() => {
  switch (props.nextCallType) {
    case "Client": return "mdi-account";
    case "Employé": return "mdi-briefcase-variant";
    case "RDV": return "mdi-phone-in-talk";
    case "Visite": return "mdi-map-marker";
    default: return "mdi-file-document";
  }
});

const displayedName = computed(() => {
  const c = props.binome?.client;
  const e = props.binome?.employee;
  
  if ((props.nextCallType === 'Visite' || props.nextCallType === 'RDV') && c && e) {
      return `${c.last_name} & ${e.last_name}`;
  }
  if (props.nextCallType === 'Employé' && e) return `${e.first_name} ${e.last_name}`;
  if (c) return `${c.first_name} ${c.last_name}`;
  return "Dossier inconnu";
});

const subtitle = computed(() => {
  switch (props.nextCallType) {
    case "Client": return "Appel Client";
    case "Employé": return "Point Intervenant";
    case "RDV": return "Planification";
    case "Visite": return "Sur le terrain";
    default: return "Action";
  }
});

// --- Styles CSS ---

const cardStyle = computed(() => {
    return {
        borderLeft: `5px solid rgb(var(--v-theme-${colorTheme.value}))`, 
        borderTop: '1px solid #F0F0F0',
        borderRight: '1px solid #F0F0F0',
        borderBottom: '1px solid #F0F0F0',
        backgroundColor: 'white',
        cursor: 'pointer',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease'
    };
});
</script>

<style scoped>
.binome-card {
  border-left-width: 5px !important;
}

.binome-card:hover {
  transform: translateX(4px); 
  box-shadow: 0 3px 10px rgba(0,0,0,0.08) !important;
}

.binome-card:hover .chevron-icon {
    color: #757575 !important;
}
</style>