export function getStateColor(state) {
    if (!state) return "grey";
    const s = state.toLowerCase();
    if (s.includes("non")) return "error";
    if (s.includes("conforme")) return "success";
    if (s.includes("appeler") || s.includes("retard")) return "grey-darken-1"; // Changé en gris pour retard
    return "grey";
}

export function getStateIcon(state) {
    if (!state) return "mdi-help-circle";
    const s = state.toLowerCase();

    if (s.includes("non")) return "mdi-close-circle";
    if (s.includes("conforme")) return "mdi-check-circle";
    if (s.includes("appeler")) return "mdi-phone";
    if (s.includes("retard")) return "mdi-clock-alert";

    return "mdi-circle-small";
}
