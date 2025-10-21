<template>
  <v-card
    :color="cardColor"
    rounded="xl"
    class="pa-4 d-flex align-center text-white mx-auto"
    max-width="380"
  >
    <!-- Icône principale -->
    <v-avatar size="48" color="white" class="mr-4">
      <v-icon size="28" :color="cardColor">
        {{ icon }}
      </v-icon>
    </v-avatar>

    <!-- Nom affiché -->
    <div>
      <div class="text-h6 font-weight-bold">
        {{ displayedName }}
      </div>
      <div class="text-caption opacity-80">
        {{ subtitle }}
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  binome: { type: Object, required: true },
  nextCallType: { type: String, required: false }, // "Client" ou "Employé"
});

// 🎨 Couleur principale selon le type d’appel
const cardColor = computed(() => {
  if (props.nextCallType === "Client") return "primary";
  if (props.nextCallType === "Employé") return "secondary";
  return "grey";
});

// 🎯 Icône selon le type d’appel
const icon = computed(() => {
  if (props.nextCallType === "Client") return "mdi-account"; // Client élégant
  if (props.nextCallType === "Employé") return "mdi-account-tie"; // Employé de maison
  return "mdi-help-circle";
});

// 🧠 Nom affiché (Prénom Nom)
const displayedName = computed(() => {
  if (props.nextCallType === "Client" && props.binome?.client) {
    return `${props.binome.client.first_name} ${props.binome.client.last_name}`;
  }
  if (props.nextCallType === "Employé" && props.binome?.employee) {
    return `${props.binome.employee.first_name} ${props.binome.employee.last_name}`;
  }
  return "Inconnu";
});

// 🗒️ Sous-titre explicite
const subtitle = computed(() => {
  if (props.nextCallType === "Client") return "Appel client à effectuer";
  if (props.nextCallType === "Employé") return "Appel intervenant à effectuer";
  return "";
});
</script>
