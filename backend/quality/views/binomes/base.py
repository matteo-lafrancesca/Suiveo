from datetime import timedelta
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ...models import Binome, Call, CallTemplate
from ...serializers import BinomeSerializer, CallSerializer
from .tableau_suivi import TableauSuiviMixin
from .planning import PlanningMixin
from .list import BinomeListMixin


class BinomeViewSet(viewsets.ModelViewSet, TableauSuiviMixin, PlanningMixin,BinomeListMixin):
    queryset = Binome.objects.all()
    serializer_class = BinomeSerializer
    permission_classes = [permissions.IsAuthenticated]

    # ============================================================
    # LOGIQUE DE MISE À JOUR DES ÉTATS
    # ============================================================
    def update_binome_state(self, binome):
        if binome.state == "Non conforme":
            return

        next_call = (
            Call.objects.filter(binome=binome, actual_date__isnull=True)
            .order_by("scheduled_date")
            .first()
        )
        if not next_call:
            return

        today = timezone.now().date()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)

        if monday <= next_call.scheduled_date <= sunday:
            new_state = "À appeler"
        elif next_call.scheduled_date < monday:
            new_state = "En retard"
        else:
            new_state = "Conforme"

        if binome.state != new_state:
            binome.state = new_state
            binome.save(update_fields=["state"])

    def update_all_binomes_states(self):
        for b in Binome.objects.all():
            self.update_binome_state(b)

    # ============================================================
    # CRUD OVERRIDES & DÉTAILS
    # ============================================================
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.update_binome_state(instance)
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Création d’un binôme + génération uniquement du premier appel (offset minimal)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        binome = serializer.save()

        # On récupère le template ayant le plus petit offset
        first_template = CallTemplate.objects.order_by("offset_weeks").first()

        if first_template:
            scheduled_date = binome.first_intervention_date + timedelta(weeks=first_template.offset_weeks)
            Call.objects.create(
                binome=binome,
                template=first_template,
                title=f"{first_template.name} du {scheduled_date.strftime('%d/%m/%Y')}",
                scheduled_date=scheduled_date,
            )

        # Met à jour l’état du binôme après création
        self.update_binome_state(binome)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="details")
    def details(self, request, pk=None):
        binome = self.get_object()
        self.update_binome_state(binome)
        calls = Call.objects.filter(binome=binome).order_by("scheduled_date")
        completed_calls = [c for c in calls if c.actual_date]
        next_calls = [c for c in calls if not c.actual_date]
        next_call = next_calls[0] if next_calls else None

        return Response({
            "binome": BinomeSerializer(binome).data,
            "completed_calls": CallSerializer(completed_calls, many=True).data,
            "next_call": CallSerializer(next_call).data if next_call else None,
        })
