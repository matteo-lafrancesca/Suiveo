<template>
  <v-app-bar
    color="white"
    flat
    height="70"
    elevation="2"
    class="position-fixed w-100"
    style="z-index: 100; top: 0; left: 0;"
  >
    <div
      class="d-flex align-center justify-space-between w-100"
      style="padding: 0 40px;"
    >
      <!-- SECTION GAUCHE -->
      <div class="d-flex align-center" style="gap: 32px;">
        <span
          class="text-h4 font-weight-bold text-primary"
          style="letter-spacing: 0.5px; padding: 0 16px;"
        >
          Suiveo
        </span>

        <div class="d-flex align-center" style="gap: 8px;">
          <v-btn
            v-for="link in links"
            :key="link.text"
            variant="text"
            color="primary"
            rounded="lg"
            class="text-body-1 font-weight-bold text-capitalize"
          >
            {{ link.text }}
          </v-btn>
        </div>
      </div>

      <!-- SECTION DROITE (icônes ou futur menu user) -->
      <div class="d-flex align-center" style="gap: 12px;">
        <v-btn icon color="primary" variant="text">
          <v-icon>mdi-bell-outline</v-icon>
        </v-btn>
        <v-btn icon color="primary" variant="text">
          <v-icon>mdi-account-circle-outline</v-icon>
        </v-btn>
      </div>
    </div>
  </v-app-bar>
</template>

<script setup>
const links = [
  { text: 'Tableau de Suivi' },
  { text: 'Planning' },
  { text: 'Liste de Binômes' },
]
</script>
