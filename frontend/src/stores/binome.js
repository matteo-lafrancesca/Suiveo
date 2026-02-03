import { defineStore } from 'pinia';
import api from '@/services/api';

export const useBinomeStore = defineStore('binome', {
    state: () => ({
        binome: null,
        completedCalls: [],
        pendingCalls: [],
        nextCall: null,
        loading: false,
        error: null,
    }),
    actions: {
        async fetchBinomeDetails(id) {
            this.loading = true;
            try {
                const { data } = await api.get(`/binomes/${id}/details/`);
                this.binome = data.binome;
                this.completedCalls = data.completed_calls || [];
                this.pendingCalls = data.pending_calls || [];
                this.nextCall = data.next_call || null;
            } catch (err) {
                this.error = err;
                console.error(err);
            } finally {
                this.loading = false;
            }
        },
        async markConforme(note) {
            if (!this.nextCall) return;
            await api.post(`/calls/${this.nextCall.id}/conforme/`, { note });
            await this.fetchBinomeDetails(this.binome.id);
        },
        async markNonConforme() {
            if (!this.nextCall) return;
            await api.post(`/calls/${this.nextCall.id}/non-conforme/`);
            await this.fetchBinomeDetails(this.binome.id);
        },
        async updateNote(newNote) {
            // Si tu as un endpoint dédié ou si tu veux juste update localement en attendant
            if (this.binome) {
                this.binome.note = newNote;
            }
        }
    }
});
