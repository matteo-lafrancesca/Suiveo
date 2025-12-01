from datetime import date, timedelta, datetime # Ajout de timedelta et datetime
from django.utils import timezone
from django.db import transaction # Ajout pour la sécurité des données
from ..models import Binome, BinomePause, Call # Ajout de Call

class PauseService:
    """
    Service dédié à la gestion des pauses et au calcul du temps suspendu.
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
        """Vérifie si le binôme est en pause active."""
        return self.binome.pauses.filter(end_date__isnull=True).exists()

    # ============================================================
    # ⏯️ ACTIONS (Start / Stop / Schedule)
    # ============================================================
    
    @transaction.atomic
    def create_pause(self, start_date: date, end_date: date):
        """
        Crée une pause définie (date début/fin) et DÉCALE tous les appels futurs.
        """
        if end_date <= start_date:
            raise ValueError("La date de fin doit être postérieure à la date de début.")

        # 1. Calcul de la durée en jours
        duration = (end_date - start_date).days

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

    def start_pause(self, start_date: date = None) -> BinomePause | None:
        """Démarre une pause indéfinie (Stop/Start manuel)."""
        if self.is_currently_paused():
            return None

        start_date = start_date or timezone.now().date()
        pause = BinomePause.objects.create(
            binome=self.binome,
            start_date=start_date,
        )

        from .binome_service import BinomeService
        if self.binome.state != "Non conforme":
            BinomeService(self.binome).update_state()

        return pause

    def stop_pause(self):
        """Clôture la pause active et relance la planification."""
        active_pause = self.binome.pauses.filter(end_date__isnull=True).first()
        if not active_pause:
            return None

        # 1. Clôture
        active_pause.end_date = timezone.now().date()
        active_pause.duration_days = (active_pause.end_date - active_pause.start_date).days
        active_pause.save()

        # 2. Nettoyage et Reprogrammation
        from .call_service import CallService
        from .binome_service import BinomeService

        CallService.remove_future_pending_calls(self.binome)

        last_completed_call = CallService.get_last_completed_call(self.binome)

        if last_completed_call:
            CallService(last_completed_call).schedule_next_call()
        else:
            CallService.schedule_first_call(self.binome)

        return BinomeService(self.binome).update_state()