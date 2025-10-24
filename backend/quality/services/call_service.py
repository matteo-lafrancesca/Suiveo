# app/services/call_service.py
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from ..models import Call, CallTemplate, BinomePause


class CallService:
    """Service métier gérant la logique des appels."""

    def __init__(self, call: Call):
        self.call = call
        self.binome = call.binome
        self.template = call.template

    # ============================================================
    # 🔁 PLANIFICATION AUTOMATIQUE
    # ============================================================
    def schedule_next_call(self):
        """Programme automatiquement le prochain appel."""
        if not self.template:
            return None

        # Si le template a une récurrence mensuelle
        if self.template.recurrence_months:
            next_date = self.call.scheduled_date + relativedelta(months=self.template.recurrence_months)
            next_template = self.template
        else:
            next_template = (
                CallTemplate.objects
                .filter(offset_weeks__gt=self.template.offset_weeks)
                .order_by("offset_weeks")
                .first()
            )
            if not next_template:
                return None
            next_date = self.binome.first_intervention_date + timedelta(weeks=next_template.offset_weeks)

        new_call = Call.objects.create(
            binome=self.binome,
            template=next_template,
            title=f"{next_template.name} du {next_date.strftime('%d/%m/%Y')}",
            scheduled_date=next_date,
        )
        return new_call

    # ============================================================
    # ✅ MARQUER COMME CONFORME
    # ============================================================
    def mark_conforme(self, note: str = "") -> Call | None:
        """Marque un appel comme conforme et planifie le suivant."""
        self.call.note = note or "Le client est satisfait de la prestation."
        self.call.actual_date = timezone.now().date()

        # Planifie le prochain appel
        new_call = self.schedule_next_call()

        # Génère le report automatique
        if new_call:
            next_date_str = new_call.scheduled_date.strftime("%d/%m/%Y")
            self.call.report = f"✅ Binôme conforme — appel suivant programmé le {next_date_str}."
        else:
            self.call.report = "✅ Binôme conforme — aucun autre appel à programmer."

        self.call.save(update_fields=["note", "actual_date", "report"])

        # Met à jour l’état du binôme
        self.binome.state = "Conforme"
        self.binome.save(update_fields=["state"])

        return new_call

    # ============================================================
    # ❌ MARQUER COMME NON CONFORME
    # ============================================================
    def mark_non_conforme(self):
        """Marque un appel comme non conforme et crée une pause."""
        BinomePause.objects.create(
            binome=self.binome,
            start_date=timezone.now().date(),
        )

        self.call.actual_date = timezone.now().date()
        self.call.report = (
            "⛔ Binôme non conforme — il est nécessaire de planifier une action "
            "corrective ou un suivi pour remettre le binôme en conformité."
        )
        self.call.save(update_fields=["actual_date", "report"])

        self.binome.state = "Non conforme"
        self.binome.save(update_fields=["state"])
