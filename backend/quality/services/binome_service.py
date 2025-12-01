from datetime import timedelta, date, datetime
from django.utils import timezone
from babel.dates import format_date
from ..models import Binome, Call
from .call_service import CallService

class BinomeService:
    """Service métier pour gérer la logique globale des binômes."""

    def __init__(self, binome: Binome, auto_update: bool = True):
        self.binome = binome
        if auto_update:
            self.update_state()

    # ============================================================
    # 🔁 ÉTATS
    # ============================================================
    def update_state(self):
        """Met à jour l’état du binôme selon le prochain appel."""
        if self.binome.state == "Non conforme":
            return self.binome.state

        # Vérifie s'il y a une pause active (Import local)
        from .pause_service import PauseService
        if PauseService(self.binome).is_currently_paused():
            return self.binome.state

        next_call = self.get_next_call()
        
        if not next_call:
            return self.binome.state

        today = timezone.now().date()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)

        if monday <= next_call.scheduled_date <= sunday:
            new_state = "À appeler"
        elif next_call.scheduled_date < monday:
            new_state = "En retard"
        else:
            new_state = "Conforme"

        if new_state != self.binome.state:
            self.binome.state = new_state
            self.binome.save(update_fields=["state"])

        return self.binome.state

    @staticmethod
    def update_all_states():
        for b in Binome.objects.all():
            BinomeService(b, auto_update=True)

    # ============================================================
    # 📅 APPELS (FONCTIONS RESTAURÉES)
    # ============================================================
    def get_calls(self):
        return Call.objects.filter(binome=self.binome).order_by("scheduled_date")

    def get_next_call(self):
        return Call.objects.filter(binome=self.binome, actual_date__isnull=True).order_by("scheduled_date").first()

    def get_last_call(self):
        return Call.objects.filter(binome=self.binome, actual_date__isnull=False).order_by("-actual_date").first()

    # ============================================================
    # 🧩 CRÉATION INITIALE
    # ============================================================
    @staticmethod
    def create_with_first_call(data: dict):
        client = data.get("client") or data.get("client_id")
        employee = data.get("employee") or data.get("employee_id")

        if Binome.objects.filter(client=client, employee=employee).exists():
            raise ValueError("Ce binôme existe déjà.")

        if isinstance(data.get("first_intervention_date"), str):
            data["first_intervention_date"] = datetime.strptime(
                data["first_intervention_date"], "%Y-%m-%d"
            ).date()

        if data["first_intervention_date"].weekday() >= 5:
            raise ValueError("La date de première intervention doit être un jour de semaine.")

        binome = Binome.objects.create(**data)

        # Délégation propre au CallService
        CallService.schedule_first_call(binome)

        BinomeService(binome).update_state()
        return binome

    # ============================================================
    # 📊 DONNÉES (Timeline / Planning / Liste)
    # ============================================================
    
    # 👇 C'est cette fonction qui manquait ! 👇
    @staticmethod
    def get_all_enriched():
        """Liste complète des binômes enrichis avec leurs appels."""
        enriched = []
        # Optimisation : select_related pour éviter trop de requêtes SQL sur client/employee
        for b in Binome.objects.select_related("client", "employee"):
            service = BinomeService(b)  # 🔄 mise à jour automatique ici
            last = service.get_last_call()
            next_ = service.get_next_call()

            enriched.append({
                "binome": b,
                "last_call": last,
                "next_call": next_,
            })
        return enriched

    def get_timeline(self):
        """Données pour la vue détail/timeline."""
        self.update_state()
        now = timezone.now().date()
        
        calls_queryset = self.get_calls()
        last_call = CallService.get_last_completed_call(self.binome)
        next_call = self.get_next_call()

        show_report = False
        if last_call:
            if self.binome.state in ["Conforme", "Non conforme"]:
                show_report = True
            elif next_call and now < next_call.scheduled_date:
                show_report = True
        
        # Sérialisation manuelle pour éviter erreur 500 JSON
        pauses_data = list(self.binome.pauses.values('id', 'start_date', 'end_date', 'duration_days'))

        return {
            "calls": calls_queryset,
            "last_call": last_call,
            "next_call": next_call,
            "show_report": show_report,
            "pauses": pauses_data,
        }

    @staticmethod
    def get_week_planning(week_number: int | None = None, year: int | None = None):
        """Planning hebdomadaire."""
        today = timezone.now().date()
        year = year or today.year
        week_number = week_number or today.isocalendar()[1]

        monday = date.fromisocalendar(year, week_number, 1)
        
        days = []
        for i in range(5):
            current_day = monday + timedelta(days=i)
            day_label = format_date(current_day, format="EEEE d MMMM", locale="fr_FR").capitalize()

            calls_today = (
                Call.objects
                .filter(scheduled_date=current_day, actual_date__isnull=True)
                .select_related("binome__client", "binome__employee", "template")
            )

            binomes_data = []
            for call in calls_today:
                BinomeService(call.binome, auto_update=True)
                binomes_data.append({
                    "binome": call.binome,
                    "call": call,
                })

            days.append({
                "date": current_day,
                "label": day_label,
                "binomes": binomes_data,
            })

        return {
            "week_number": week_number,
            "year": year,
            "monday": monday,
            "friday": monday + timedelta(days=4),
            "days": days,
        }