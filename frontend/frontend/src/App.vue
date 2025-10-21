<template>
  <v-app>
    <div class="app-shell">
      <Header />
      <v-main class="main">
        <router-view />
      </v-main>
    </div>
  </v-app>
</template>

<script setup>
import Header from './components/Header.vue'
</script>

<!-- RÈGLES GLOBALES (non scoped) : masquent la scrollbar de la page -->
<style>
html, body, #app {
  margin: 0;
  height: 100%;
  overflow: hidden;        /* supprime le scroll global */
}

/* Vuetify doit aussi être full height et sans scroll global */
.v-application, .v-application--wrap {
  height: 100%;
  overflow: hidden;
}

/* Optionnel : cacher visuellement la barre si un overflow s'affiche quand même */
body::-webkit-scrollbar { display: none; }
body { -ms-overflow-style: none; scrollbar-width: none; }
</style>

<!-- RÈGLES DU COMPOSANT -->
<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;        /* pas de scroll global */
}

.main {
  flex: 1 1 auto;
  overflow: hidden;        /* le scroll se gère à l’intérieur des colonnes */
  display: flex;
  flex-direction: column;
}
</style>
