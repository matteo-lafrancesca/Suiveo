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

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;        /* page pleine hauteur */
  overflow: hidden;     /* pas de scroll global */
}

.main {
  flex: 1 1 auto;       /* prend tout l’espace restant */
  overflow: hidden;     /* le scroll se gère à l’intérieur de tes colonnes */
}
</style>
