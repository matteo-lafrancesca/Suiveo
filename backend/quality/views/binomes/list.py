# app/views/binomes/list.py
from rest_framework.decorators import action
from rest_framework.response import Response
from ...models import Binome, Call
from ...serializers import BinomeSerializer


class BinomeListMixin:
    """Mixin pour renvoyer la liste enrichie des binômes."""

    @action(detail=False, methods=["get"], url_path="enrichis")
    def binome_list(self, request):
        """
        Renvoie les binômes enrichis avec :
        - dernier appel (last_call)
        - prochain appel (next_call)
        - semaine du prochain appel
        """
        self.update_all_binomes_states()

        binomes = Binome.objects.select_related("client", "employee").all()
        enriched = []

        for b in binomes:
            # Dernier appel effectué
            last_call = (
                Call.objects.filter(binome=b, actual_date__isnull=False)
                .select_related("template")
                .order_by("-actual_date")
                .first()
            )

            # Prochain appel à venir
            next_call = (
                Call.objects.filter(binome=b, actual_date__isnull=True)
                .select_related("template")
                .order_by("scheduled_date")
                .first()
            )

            data = BinomeSerializer(b).data

            data["last_call"] = (
                {
                    "template_name": last_call.template.name if last_call.template else "—",
                    "actual_date": last_call.actual_date,
                }
                if last_call
                else None
            )

            data["next_call"] = (
                {
                    "template_name": next_call.template.name if next_call.template else "—",
                    "template_type": next_call.template.type if next_call.template else None,
                    "scheduled_date": next_call.scheduled_date,
                    "week_number": next_call.scheduled_date.isocalendar()[1],
                }
                if next_call
                else None
            )

            enriched.append(data)

        return Response(enriched)
