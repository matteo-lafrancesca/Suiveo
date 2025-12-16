from datetime import date, timedelta, datetime
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Binome, BinomePause, Call

class PauseService:
    """
    Service dédié à la gestion des pauses et au calcul du temps suspendu.
    Toutes les pauses sont en multiples de 7 jours (semaines complètes).
    """

    def __init__(self, binome: Binome):
        self.binome = binome

    # ============================================================
    # 🧮 CALCULS (Utilisé par CallService)
    # ============================================================
    def get_total_delay(self, since_date: date = None) -> int:
        """
        Calcule le nombre total de jours de pause terminées.
        :param since_date: Si fourni, ne compte que les pauses ayant commencé APRES cette date.
        """
        pauses = self.binome.pauses.filter(end_date__isnull=False)
        
        if since_date:
            pauses = pauses.filter(start_date__gte=since_date)

        total_days = 0
        for pause in pauses:
            if pause.start_date and pause.end_date:
                total_days += (pause.end_date - pause.start_date).days
        
        return total_days

    def is_currently_paused(self) -> bool:
        """Vérifie si le binôme est en pause active (non-conformité uniquement)."""
        return self.binome.pauses.filter(end_date__isnull=True).exists()

    # ============================================================
    # ⏯️ ACTIONS (Start / Stop / Schedule)
    # ============================================================
    
    @transaction.atomic
    def create_pause(self, start_date: date, end_date: date):
        """
        Crée une pause planifiée (date début/fin) et DÉCALE tous les appels futurs.
        La durée doit être un multiple de 7 jours.
        """
        if end_date <= start_date:
            raise ValueError("La date de fin doit être postérieure à la date de début.")

        # 1. Calcul de la durée en jours
        duration = (end_date - start_date).days

        # --- Validation métier ---
        if duration % 7 != 0:
            raise ValueError("La durée de la pause doit être un multiple de 7 jours (semaines complètes).")
            
        if start_date.weekday() != self.binome.first_intervention_date.weekday():
            # On récupère le nom du jour attendu pour le message d'erreur
            days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
            expected_day = days[self.binome.first_intervention_date.weekday()]
            raise ValueError(f"La pause doit commencer un {expected_day} (jour de l'intervention).")
        # -------------------------

        # 2. Création de la pause
        pause = BinomePause.objects.create(
            binome=self.binome,
            start_date=start_date,
            end_date=end_date,
            duration_days=duration
        )

        # 3. DÉCALAGE DES APPELS FUTURS
        # On cible les appels NON réalisés dont la date est >= au début de la pause
        future_calls = Call.objects.filter(
            binome=self.binome,
            actual_date__isnull=True,
            scheduled_date__gte=start_date
        )

        for call in future_calls:
            call.scheduled_date += timedelta(days=duration)
            call.save(update_fields=["scheduled_date"])

        # 4. Mise à jour de l'état
        from .binome_service import BinomeService
        BinomeService(self.binome).update_state()

        return pause

    def start_pause(self, start_date: date = None) -> BinomePause:
        """
        Démarre une pause indéfinie (non-conformité uniquement).
        Cette pause sera arrêtée via stop_pause() avec arrondi automatique.
        """
        if self.is_currently_paused():
            raise ValidationError("Une pause est déjà active pour ce binôme.")

        start_date = start_date or timezone.now().date()
        pause = BinomePause.objects.create(
            binome=self.binome,
            start_date=start_date,
        )

        return pause

    def stop_pause(self):
        """
        Clôture la pause active avec arrondi automatique au multiple de 7 inférieur.
        Décale les appels futurs de la durée finale de la pause.
        - Si < 7 jours : pause supprimée, aucun décalage
        - Si >= 7 jours : arrondi au multiple de 7 inférieur (ex: 15j → 14j), appels décalés
        """
        active_pause = self.binome.pauses.filter(end_date__isnull=True).first()
        if not active_pause:
            raise ValidationError("Aucune pause active à arrêter pour ce binôme.")

        # 1. Calcul de la durée réelle
        end_date = timezone.now().date()
        duration_days = (end_date - active_pause.start_date).days

        # 2. Arrondi au multiple de 7 inférieur
        if duration_days < 7:
            # Moins d'une semaine : suppression de la pause, aucun décalage
            active_pause.delete()
            shift_days = 0
        else:
            # Arrondi inférieur : 8j → 7j, 14j → 14j, 15j → 14j
            rounded_duration = (duration_days // 7) * 7
            
            active_pause.end_date = active_pause.start_date + timedelta(days=rounded_duration)
            active_pause.duration_days = rounded_duration
            active_pause.save()
            shift_days = rounded_duration

        # 3. Décaler les appels futurs (non réalisés) de la durée de la pause
        if shift_days > 0:
            future_calls = Call.objects.filter(
                binome=self.binome,
                actual_date__isnull=True,
                scheduled_date__gte=active_pause.start_date
            )
            
            for call in future_calls:
                call.scheduled_date += timedelta(days=shift_days)
                call.save(update_fields=["scheduled_date"])

        # 4. Mise à jour de l'état
        from .binome_service import BinomeService
        return BinomeService(self.binome).update_state()