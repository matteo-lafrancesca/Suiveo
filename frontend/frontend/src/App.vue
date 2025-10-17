<template>
  <v-app>
    <Header />

    <!-- NOTE IMPORTANTE : on supprime le comportement "offset" de Vuetify -->
    <v-main class="remove-offset">
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import Header from './components/Header.vue'
</script>

<style>
/* Vuetify ajoute un padding-top égal à la hauteur de l'app-bar.
   On l’enlève pour forcer le contenu à être centré. */
.remove-offset {
  padding-top: 0 !important;
  margin-top: 0 !important;
  height: 100vh;
  overflow: hidden;
}
</style>
