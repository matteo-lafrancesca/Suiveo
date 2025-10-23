<template>
  <v-card
    :color="cardColor"
    rounded="xl"
    class="pa-4 d-flex align-center text-white mx-auto hover-card"
    max-width="380"
    @click="goToBinome"
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
import { useRouter } from "vue-router";

const router = useRouter();

const props = defineProps({
  binome: { type: Object, required: true },
  nextCallType: { type: String, required: false }, // "Client", "Employé", "RDV", "Visite"
});

// 🎨 Couleur principale selon le type d’appel
const cardColor = computed(() => {
  switch (props.nextCallType) {
    case "Client":
      return "primary"; // bleu
    case "Employé":
      return "secondary"; // violet
    case "RDV":
      return "#f59e0b"; // orange
    case "Visite":
      return "#10b981"; // vert
    default:
      return "#9ca3af"; // gris neutre
  }
});

// 🎯 Icône selon le type d’appel
const icon = computed(() => {
  switch (props.nextCallType) {
    case "Client":
      return "mdi-account";
    case "Employé":
      return "mdi-account-tie";
    case "RDV":
      return "mdi-phone"; // prise de rendez-vous
    case "Visite":
      return "mdi-home"; // visite sur site
    default:
      return "mdi-help-circle";
  }
});

// 🧠 Nom affiché selon le type
const displayedName = computed(() => {
  const c = props.binome?.client;
  const e = props.binome?.employee;
  switch (props.nextCallType) {
    case "Client":
      return c ? `${c.first_name} ${c.last_name}` : "Client inconnu";
    case "Employé":
      return e ? `${e.first_name} ${e.last_name}` : "Employé inconnu";
    default:
      // Si RDV ou Visite : afficher les deux
      return c && e ? `${c.first_name} ${c.last_name} – ${e.first_name}` : "Binôme inconnu";
  }
});

// 🗒️ Sous-titre explicite
const subtitle = computed(() => {
  switch (props.nextCallType) {
    case "Client":
      return "Appel client à effectuer";
    case "Employé":
      return "Appel intervenant à effectuer";
    case "RDV":
      return "Prise de rendez-vous à planifier";
    case "Visite":
      return "Visite sur site à effectuer";
    default:
      return "";
  }
});

// 🚀 Navigation vers la fiche du binôme
function goToBinome() {
  if (props.binome?.id) router.push(`/binome/${props.binome.id}`);
}
</script>

<style scoped>
.hover-card {
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.2s ease;
}
.hover-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
</style>
