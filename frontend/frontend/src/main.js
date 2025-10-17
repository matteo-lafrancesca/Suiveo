// --- Import Vue ---
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'


// --- Import Vuetify ---
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// --- Import CSS global (avec police DM Sans) ---
import './assets/main.css'

// --- Création de l'instance Vuetify ---
const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#2a4252', 
          secondary: '#a78bfa', 
          background: '#f8fafc',
          surface: '#ffffff', 
          error: '#d3251fff',
          success: '#22c55e',
        },
      },
    },
  },
})

// --- Création de l'app Vue ---
const app = createApp(App)

app.use(vuetify)
app.use(router)
app.mount('#app')
