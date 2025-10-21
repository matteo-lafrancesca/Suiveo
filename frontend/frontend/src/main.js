// --- Import Vue ---
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// --- Import Vuetify ---
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// --- Import du set d’icônes MDI ---
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

// --- Import CSS global (avec police DM Sans) ---
import './assets/main.css'

// --- Création de l'instance Vuetify ---
const vuetify = createVuetify({
  components,
  directives,

  // ✅ Configuration du thème
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#2a4252',   // bleu-gris profond (identité principale)
          secondary: '#445b56', // vert-de-gris sombre, naturel et sobre
          background: '#f8fafc', // fond clair légèrement bleuté
          surface: '#ffffff',   // surfaces neutres
          error: '#d94a4a',     // rouge adouci
          success: '#28a870',   // vert moderne et neutre
          warning: '#e0a84f',   // jaune doux (doré mat)
        },
      },
    },
  },

  // ✅ Configuration du set d’icônes
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi },
  },
})

// --- Création de l'app Vue ---
const app = createApp(App)

app.use(vuetify)
app.use(router)
app.mount('#app')
