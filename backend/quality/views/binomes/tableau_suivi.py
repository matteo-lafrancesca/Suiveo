from rest_framework.decorators import action
from rest_framework.response import Response
from ...models import Binome, Call
from ...serializers import BinomeSerializer


class TableauSuiviMixin:
    """Mixin pour renvoyer les binômes triés par état."""

    @action(detail=False, methods=["get"], url_path="tableau-suivi")
    def tableau_suivi(self, request):
        self.update_all_binomes_states()

        binomes = Binome.objects.select_related("client", "employee").all()
        grouped = {"en_retard": [], "a_appeler": [], "non_conformes": []}

        for b in binomes:
            serialized = BinomeSerializer(b).data
            next_call = (
                Call.objects.filter(binome=b, actual_date__isnull=True)
                .select_related("template")
                .order_by("scheduled_date")
                .first()
            )

            serialized["client_name"] = f"{b.client.first_name} {b.client.last_name}"
            serialized["employee_name"] = f"{b.employee.first_name} {b.employee.last_name}"

            serialized["next_call"] = (
                {
                    "template_name": next_call.template.name,
                    "template_type": next_call.template.type,
                    "scheduled_date": next_call.scheduled_date,
                    "week_number": next_call.scheduled_date.isocalendar()[1],
                }
                if next_call and next_call.template
                else None
            )

            grouped_key = {
                "En retard": "en_retard",
                "À appeler": "a_appeler",
                "Non conforme": "non_conformes",
            }.get(b.state)

            if grouped_key:
                grouped[grouped_key].append(serialized)

        return Response(grouped)
