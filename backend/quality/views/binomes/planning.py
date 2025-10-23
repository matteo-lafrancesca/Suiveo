from datetime import timedelta, date
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from ...models import Binome, Call
from ...serializers import BinomeSerializer
import locale

try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except:
    pass


class PlanningMixin:
    """Mixin pour générer le planning hebdomadaire."""

    @action(detail=False, methods=["get"], url_path="planning")
    def planning(self, request):
        today = timezone.now().date()
        week_number = int(request.query_params.get("week", today.isocalendar()[1]))
        year = today.year
        monday = date.fromisocalendar(year, week_number, 1)
        friday = monday + timedelta(days=4)

        self.update_all_binomes_states()

        binomes = Binome.objects.select_related("client", "employee").prefetch_related("calls__template")
        days = []

        for i in range(5):
            current_day = monday + timedelta(days=i)
            label = current_day.strftime("%A %d %B").capitalize()
            binomes_du_jour = []

            for b in binomes:
                next_call = (
                    Call.objects.filter(
                        binome=b,
                        actual_date__isnull=True,
                        scheduled_date=current_day,
                    )
                    .select_related("template")
                    .first()
                )

                if next_call:
                    serialized = BinomeSerializer(b).data
                    serialized["client_name"] = f"{b.client.first_name} {b.client.last_name}"
                    serialized["employee_name"] = f"{b.employee.first_name} {b.employee.last_name}"
                    serialized["next_call"] = {
                        "template_name": next_call.template.name,
                        "template_type": next_call.template.type,
                        "scheduled_date": next_call.scheduled_date,
                    }
                    binomes_du_jour.append(serialized)

            days.append({
                "date": current_day.strftime("%Y-%m-%d"),
                "label": label,
                "binomes": binomes_du_jour,
            })

        return Response({
            "week_number": week_number,
            "monday": monday.strftime("%Y-%m-%d"),
            "friday": friday.strftime("%Y-%m-%d"),
            "days": days,
        })
