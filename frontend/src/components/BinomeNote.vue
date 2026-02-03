<template>
  <v-sheet class="pa-4 rounded-lg bg-grey-lighten-4 border-dashed mb-6">
    
    <div class="d-flex align-center justify-space-between mb-2">
      <div class="d-flex align-center">
        <v-icon size="16" class="mr-2 text-medium-emphasis">mdi-text-box-outline</v-icon>
        <span class="text-caption font-weight-bold text-medium-emphasis text-uppercase">Informations utiles</span>
      </div>
      
      <v-btn 
        v-if="!isEditing"
        icon="mdi-pencil" 
        size="x-small" 
        variant="text" 
        color="primary" 
        density="comfortable"
        @click="startEdit"
        tooltip="Modifier la note"
      />
    </div>

    <div 
      v-if="!isEditing" 
      class="text-body-2 text-medium-emphasis text-pre-wrap" 
      style="line-height: 1.6;"
    >
      {{ note || "Aucune note particulière pour ce dossier." }}
    </div>

    <div v-else>
      <v-textarea
        v-model="localNote"
        variant="outlined"
        bg-color="white"
        color="primary"
        density="compact"
        rows="3"
        auto-grow
        hide-details
        class="mb-3"
        placeholder="Saisissez les informations ici..."
        autofocus
      ></v-textarea>
      
      <div class="d-flex justify-end gap-2">
        <v-btn 
          size="small" 
          variant="text" 
          color="grey-darken-1" 
          class="mr-2"
          @click="cancelEdit"
          :disabled="saving"
        >
          Annuler
        </v-btn>
        <v-btn 
          size="small" 
          color="primary" 
          variant="flat"
          @click="save"
          :loading="saving"
        >
          Valider
        </v-btn>
      </div>
    </div>

  </v-sheet>
</template>

<script setup>
import { ref } from 'vue';
import api from "@/services/api";

const props = defineProps({
  binomeId: { type: [Number, String], required: true },
  note: { type: String, default: "" }
});

const emit = defineEmits(['update:note']);

const isEditing = ref(false);
const localNote = ref("");
const saving = ref(false);

function startEdit() {
  localNote.value = props.note || "";
  isEditing.value = true;
}

function cancelEdit() {
  isEditing.value = false;
  localNote.value = "";
}

async function save() {
  saving.value = true;
  try {
    await api.patch(`/binomes/${props.binomeId}/`, { 
      note: localNote.value 
    });
    
    // On notifie le parent que la note a changé pour qu'il mette à jour ses données
    emit('update:note', localNote.value);
    isEditing.value = false;
  } catch (e) {
    console.error("Erreur lors de la sauvegarde de la note", e);
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.border-dashed {
  border: 1px dashed rgba(0, 0, 0, 0.12) !important;
}

.text-pre-wrap {
  white-space: pre-wrap; 
  word-break: break-word; 
}
</style>