# app/services/binome_service.py
from datetime import timedelta, date, datetime
from django.utils import timezone
from ..models import Binome, Call, CallTemplate
from babel.dates import format_date


class BinomeService:
    """Service métier pour gérer la logique complète des binômes."""

    def __init__(self, binome: Binome, auto_update: bool = True):
        self.binome = binome
        # 🔁 Met automatiquement à jour l’état dès qu’un service est instancié
        if auto_update:
            self.update_state()

    # ============================================================
    # 🔁 États
    # ============================================================
    def update_state(self):
        """Met à jour l’état du binôme selon le prochain appel."""
        if self.binome.state == "Non conforme":
            return self.binome.state

        next_call = (
            Call.objects.filter(binome=self.binome, actual_date__isnull=True)
            .order_by("scheduled_date")
            .first()
        )
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
        """Met à jour tous les binômes."""
        for b in Binome.objects.all():
            BinomeService(b, auto_update=True)

    # ============================================================
    # 📅 Appels
    # ============================================================
    def get_calls(self):
        return Call.objects.filter(binome=self.binome).order_by("scheduled_date")

    def get_next_call(self):
        return (
            Call.objects.filter(binome=self.binome, actual_date__isnull=True)
            .order_by("scheduled_date")
            .first()
        )

    def get_last_call(self):
        return (
            Call.objects.filter(binome=self.binome, actual_date__isnull=False)
            .order_by("-actual_date")
            .first()
        )

    # ============================================================
    # 🧩 Création initiale
    # ============================================================
    @staticmethod
    def create_with_first_call(data: dict):
        """Crée un binôme et génère uniquement le premier appel."""
        client = data.get("client") or data.get("client_id")
        employee = data.get("employee") or data.get("employee_id")

        # 🔹 Vérifie doublon
        existing = Binome.objects.filter(client=client, employee=employee).first()
        if existing:
            raise ValueError("Ce binôme existe déjà entre ce client et cet employé.")

        # 🔹 Convertit la date si elle est une chaîne
        if isinstance(data.get("first_intervention_date"), str):
            data["first_intervention_date"] = datetime.strptime(
                data["first_intervention_date"], "%Y-%m-%d"
            ).date()

        # 🔹 Vérifie que la date n’est pas un week-end
        weekday = data["first_intervention_date"].weekday()  # 0 = lundi, 6 = dimanche
        if weekday >= 5:
            raise ValueError(
                "La date de première intervention doit être un jour de semaine (lundi à vendredi)."
            )

        # 🔹 Crée le binôme
        binome = Binome.objects.create(**data)

        # 🔹 Crée le premier appel si template disponible
        first_template = CallTemplate.objects.order_by("offset_weeks").first()
        if first_template:
            scheduled_date = binome.first_intervention_date + timedelta(
                weeks=first_template.offset_weeks
            )
            Call.objects.create(
                binome=binome,
                template=first_template,
                title=f"{first_template.name} du {scheduled_date.strftime('%d/%m/%Y')}",
                scheduled_date=scheduled_date,
            )

        BinomeService(binome).update_state()
        return binome

    # ============================================================
    # 📊 Timeline / planning / liste
    # ============================================================
    def get_timeline(self):
        """Retourne les données nécessaires à la timeline du binôme."""
        self.update_state()

        now = timezone.now().date()
        calls = list(self.get_calls())
        last_call = self.get_last_call()
        next_call = self.get_next_call()

        show_report = False
        if last_call:
            if self.binome.state in ["Conforme", "Non conforme"]:
                show_report = True
            elif next_call and now < next_call.scheduled_date:
                show_report = True

        return {
            "calls": calls,
            "last_call": last_call,
            "next_call": next_call,
            "show_report": show_report,
        }

    @staticmethod
    def get_all_enriched():
        """Liste complète des binômes enrichis avec leurs appels."""
        enriched = []
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

    @staticmethod
    def get_week_planning(week_number: int | None = None, year: int | None = None):
        """Planning hebdomadaire (Lundi → Vendredi)"""
        today = timezone.now().date()
        year = year or today.year
        week_number = week_number or today.isocalendar()[1]

        monday = date.fromisocalendar(year, week_number, 1)
        friday = monday + timedelta(days=4)

        days = []
        for i in range(5):
            current_day = monday + timedelta(days=i)

            # ✅ Formatage français propre
            day_label = format_date(current_day, format="EEEE d MMMM", locale="fr_FR").capitalize()

            binomes = []
            for b in Binome.objects.select_related("client", "employee"):
                # 🧠 Chaque BinomeService met automatiquement à jour l’état
                service = BinomeService(b)
                call = (
                    Call.objects.filter(
                        binome=b,
                        actual_date__isnull=True,
                        scheduled_date=current_day,
                    )
                    .select_related("template")
                    .first()
                )
                if call:
                    binomes.append({
                        "binome": b,
                        "call": call,
                    })

            days.append({
                "date": current_day,
                "label": day_label,
                "binomes": binomes,
            })

        return {
            "week_number": week_number,
            "year": year,
            "monday": monday,
            "friday": friday,
            "days": days,
        }
