<template>
  <v-app-bar
    color="white"
    flat
    height="80"
    elevation="2"
    class="w-100"
  >
    <div
      class="d-flex align-center justify-space-between w-100"
      style="padding: 0 40px;"
    >
      <!-- SECTION GAUCHE -->
      <div class="d-flex align-center" style="gap: 32px;">
        <RouterLink
          to="/"
          class="text-decoration-none"
        >
          <span
            class="text-h4 font-weight-bold text-primary cursor-pointer"
            style="letter-spacing: 0.5px; padding: 0 16px;"
          >
            Suiveo
          </span>
        </RouterLink>

        <div class="d-flex align-center" style="gap: 8px;">
          <v-btn
            v-for="link in links"
            :key="link.text"
            :to="link.to"
            variant="text"
            color="primary"
            rounded="lg"
            class="text-body-1 font-weight-bold text-capitalize"
            router
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
  { text: 'Tableau de Suivi', to: '/tableau-suivi' },
  { text: 'Planning', to: '/planning' },
  { text: 'Liste de Binômes', to: '/liste-binomes' },
];
</script>
