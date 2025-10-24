# app/views/calls.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from ..models import Call
from ..serializers import CallSerializer
from ..services.call_service import CallService


class CallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all().select_related("template", "binome")
    serializer_class = CallSerializer
    permission_classes = [permissions.IsAuthenticated]

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

        return Response({"success": True, "call": CallSerializer(call).data})

    # ============================================================
    # ✅ Marquer comme conforme
    # ============================================================
    @action(detail=True, methods=["post"], url_path="conforme")
    def conforme(self, request, pk=None):
        call = self.get_object()
        service = CallService(call)
        next_call = service.mark_conforme(note=request.data.get("note", ""))

        # 🔹 Recharge le binôme depuis la base pour être sûr d’avoir le state à jour
        call.binome.refresh_from_db()

        return Response({
            "success": True,
            "message": "Appel marqué comme conforme.",
            "next_call": CallSerializer(next_call).data if next_call else None,
            "report": call.report,
            "binome_state": call.binome.state,
        })

    # ============================================================
    # ❌ Marquer comme non conforme
    # ============================================================
    @action(detail=True, methods=["post"], url_path="non-conforme")
    def non_conforme(self, request, pk=None):
        call = self.get_object()
        service = CallService(call)
        service.mark_non_conforme()

        return Response({
            "success": True,
            "message": "Binôme marqué comme non conforme et pause créée.",
            "report": call.report,
        })
