<template>
  <v-app>
    <!-- ✅ Header fixé en haut -->
    <Header class="fixed-header" />

    <!-- ✅ Contenu scrollable uniquement ici -->
  <v-main class="scrollable-main" :style="{ '--v-layout-top': '0px' }">
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import Header from './components/Header.vue'
</script>

<style>
/* ===============================
   🔹 Structure globale
================================= */
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;

  /* Empêche le scroll global du navigateur */
  overflow: hidden;
  background-color: #f8fafc;
}

/* ===============================
   🔹 Header fixé
================================= */
.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 80px; /* même hauteur que ton app-bar */
}

/* ===============================
   🔹 Scroll interne sur le contenu
================================= */
.scrollable-main {
  position: relative;
  top: 80px; /* décalé sous le header */
  height: calc(100vh - 80px); /* occupe le reste de l’écran */
  overflow-y: auto;
  overflow-x: hidden;
  padding: 24px 32px;
  background-color: #f8fafc;
  box-sizing: border-box;
}

/* ===============================
   🔹 Style scrollbar : visible uniquement sur le contenu
================================= */

/* Chrome / Edge / Safari */
.scrollable-main::-webkit-scrollbar {
  width: 8px;
  background: transparent;
}

.scrollable-main::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.25);
  border-radius: 8px;
  transition: background 0.3s ease;
}

.scrollable-main::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.4);
}

/* Firefox */
.scrollable-main {
  scrollbar-width: thin;
  scrollbar-color: rgba(0,0,0,0.25) transparent;
}

/* ===============================
   🔹 Masque la scrollbar du navigateur
================================= */
html::-webkit-scrollbar {
  width: 0px;
  background: transparent;
}

html {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
</style>
