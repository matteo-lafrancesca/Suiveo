from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from ..models import Call, CallTemplate, Binome
from .pause_service import PauseService

class CallService:
    """Service métier gérant la création et la planification des appels."""

    def __init__(self, call: Call):
        self.call = call
        self.binome = call.binome
        self.template = call.template
        self.pause_service = PauseService(self.binome)

    # ============================================================
    # 🛠️ UTILITAIRES STATIQUES
    # ============================================================
    @staticmethod
    def get_last_completed_call(binome: Binome):
        """Récupère le dernier appel réalisé (avec date réelle)."""
        return Call.objects.filter(binome=binome, actual_date__isnull=False).order_by("-actual_date").first()

    @staticmethod
    def remove_future_pending_calls(binome: Binome):
        """Supprime les appels prévus mais non réalisés."""
        Call.objects.filter(binome=binome, actual_date__isnull=True).delete()

    @staticmethod
    def schedule_first_call(binome: Binome):
        """
        Logique centralisée pour créer le TOUT premier appel.
        Utilisé à la création du binôme ET lors d'un retour de pause précoce.
        """
        # CORRECTION ICI : On filtre pour exclure les templates manuels (offset_weeks=None)
        first_template = CallTemplate.objects.filter(offset_weeks__isnull=False).order_by("offset_weeks").first()
        
        if not first_template:
            return None

        # Calcul du décalage dû aux pauses éventuelles
        pause_delay = PauseService(binome).get_total_delay()
        
        # Date = Début prestation + Offset Template + Pauses
        scheduled_date = binome.first_intervention_date + timedelta(weeks=first_template.offset_weeks) + timedelta(days=pause_delay)

        return Call.objects.create(
            binome=binome,
            template=first_template,
            title=f"{first_template.name} du {scheduled_date.strftime('%d/%m/%Y')}",
            scheduled_date=scheduled_date,
        )
    # ============================================================
    # ➕ CRÉATION MANUELLE (NOUVEAU)
    # ============================================================
    @staticmethod
    def create_manual_call(binome, template_id, scheduled_date, title=None):
        template = CallTemplate.objects.get(pk=template_id)
        
        # Si aucun titre fourni, on prend le nom du template
        final_title = title or f"{template.name} (Manuel)"
        
        return Call.objects.create(
            binome=binome,
            template=template,
            scheduled_date=scheduled_date,
            title=final_title
        )

    # ============================================================
    # 🔁 PLANIFICATION AUTOMATIQUE
    # ============================================================
    def schedule_next_call(self):
        """Programme le prochain appel en tenant compte des pauses."""
        
        if self.pause_service.is_currently_paused():
            return None

        if not self.template:
            return None

        # --- 🛡️ GARDE-FOU 🛡️ ---
        # Si le template est purement manuel (pas d'offset, pas de récurrence),
        # on ne déclenche PAS de suite automatique.
        if self.template.offset_weeks is None and self.template.recurrence_months is None:
            return None
        # ------------------------

        next_date = None
        next_template = None
        
        # 🔄 CAS 1 : Récurrence mensuelle
        if self.template.recurrence_months:
            base_date = self.call.scheduled_date + relativedelta(months=self.template.recurrence_months)
            # Ajout des pauses survenues DEPUIS l'appel précédent
            pause_delay = self.pause_service.get_total_delay(since_date=self.call.scheduled_date)
            
            next_date = base_date + timedelta(days=pause_delay)
            next_template = self.template

        # 📑 CAS 2 : Séquence (Offset par rapport au début)
        else:
            next_template = (
                CallTemplate.objects
                .filter(offset_weeks__gt=self.template.offset_weeks)
                .order_by("offset_weeks")
                .first()
            )
            if not next_template:
                return None
            
            theoretical_date = self.binome.first_intervention_date + timedelta(weeks=next_template.offset_weeks)
            total_pause_delay = self.pause_service.get_total_delay()
            
            next_date = theoretical_date + timedelta(days=total_pause_delay)

        if next_date and next_template:
            return Call.objects.create(
                binome=self.binome,
                template=next_template,
                title=f"{next_template.name} du {next_date.strftime('%d/%m/%Y')}",
                scheduled_date=next_date,
            )
        return None

    # ============================================================
    # ✅ CONFORMITÉ / ❌ NON-CONFORMITÉ
    # ============================================================
    def mark_conforme(self, note: str = "") -> Call | None:
        self.call.note = note or "Le client est satisfait de la prestation."
        self.call.actual_date = timezone.now().date()

        new_call = self.schedule_next_call()

        if new_call:
            next_str = new_call.scheduled_date.strftime("%d/%m/%Y")
            self.call.report = f"✅ Binôme conforme — appel suivant programmé le {next_str}."
        elif self.pause_service.is_currently_paused():
            self.call.report = "⏸️ Binôme en pause — planification suspendue."
        else:
            self.call.report = "✅ Binôme conforme — aucun autre appel à programmer."

        self.call.save(update_fields=["note", "actual_date", "report"])
        
        # Mise à jour état binôme
        from .binome_service import BinomeService
        BinomeService(self.binome).update_state()
        
        return new_call

    def mark_non_conforme(self):
        # 1. Créer la pause via le service dédié
        self.pause_service.start_pause()

        # 2. Mettre à jour l'appel
        self.call.actual_date = timezone.now().date()
        self.call.report = (
            "⛔ Binôme non conforme — Action corrective requise. "
            "Le binôme est mis en pause le temps de la régularisation."
        )
        self.call.save(update_fields=["actual_date", "report"])

        # 3. Forcer l'état
        self.binome.state = "Non conforme"
        self.binome.save(update_fields=["state"])