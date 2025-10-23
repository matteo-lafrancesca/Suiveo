from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Call, CallTemplate, BinomePause
from ..serializers import CallSerializer
from .binomes.base import BinomeViewSet


class CallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all().select_related("template", "binome")
    serializer_class = CallSerializer
    permission_classes = [permissions.IsAuthenticated]

    # ============================================================
    # 🔁 Fonction interne : Planifier l'appel suivant
    # ============================================================
    def schedule_next_call(self, call):
        """Programme automatiquement l’appel suivant selon le template."""
        template = call.template
        binome = call.binome

        # Si le template a une récurrence, on recrée le même appel après X mois
        if template.recurrence_months:
            next_date = call.scheduled_date + relativedelta(months=template.recurrence_months)
            new_call = Call.objects.create(
                binome=binome,
                template=template,
                title=f"{template.name} du {next_date.strftime('%d/%m/%Y')}",
                scheduled_date=next_date,
            )
            return new_call

        # Sinon, on prend le template suivant (offset supérieur)
        next_template = (
            CallTemplate.objects.filter(offset_weeks__gt=template.offset_weeks)
            .order_by("offset_weeks")
            .first()
        )

        if not next_template:
            return None  # Plus d'appel à planifier

        next_date = binome.first_intervention_date + timedelta(weeks=next_template.offset_weeks)
        new_call = Call.objects.create(
            binome=binome,
            template=next_template,
            title=f"{next_template.name} du {next_date.strftime('%d/%m/%Y')}",
            scheduled_date=next_date,
        )
        return new_call

    # ============================================================
    # 🔄 Reprogrammer un appel
    # ============================================================
    @action(detail=True, methods=["post"], url_path="reprogrammer")
    def reprogrammer(self, request, pk=None):
        call = self.get_object()
        new_date = request.data.get("new_date")
        if not new_date:
            return Response({"error": "Nouvelle date requise"}, status=400)

        call.scheduled_date = new_date
        call.title = f"{call.template.name} du {new_date}"
        call.save(update_fields=["scheduled_date", "title"])

        BinomeViewSet().update_binome_state(call.binome)
        return Response({"success": True, "call": CallSerializer(call).data})

    # ============================================================
    # ✅ Marquer un appel comme conforme
    # ============================================================
    @action(detail=True, methods=["post"], url_path="conforme")
    def conforme(self, request, pk=None):
        call = self.get_object()

        # On enregistre le compte-rendu si fourni
        note = request.data.get("note", "")
        call.note = note
        call.actual_date = timezone.now().date()
        call.save()

        # Programme l'appel suivant
        new_call = self.schedule_next_call(call)

        # Met à jour l'état du binôme
        binome = call.binome
        binome.state = "Conforme"
        binome.save(update_fields=["state"])

        return Response({
            "success": True,
            "message": "Appel marqué comme conforme.",
            "next_call": CallSerializer(new_call).data if new_call else None,
        })

    # ============================================================
    # ❌ Marquer un appel comme non conforme
    # ============================================================
    @action(detail=True, methods=["post"], url_path="non-conforme")
    def non_conforme(self, request, pk=None):
        call = self.get_object()
        binome = call.binome

        # Crée une pause
        BinomePause.objects.create(
            binome=binome,
            start_date=timezone.now().date(),
        )

        # Met le binôme en non conforme
        binome.state = "Non conforme"
        binome.save(update_fields=["state"])

        return Response({
            "success": True,
            "message": "Binôme marqué comme non conforme et pause créée.",
        })
