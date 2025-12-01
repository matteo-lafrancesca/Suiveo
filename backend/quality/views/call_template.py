# app/views/call_templates.py
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import CallTemplate
from ..serializers import CallTemplateSerializer


class CallTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet en lecture seule pour les templates d'appel.
    """
    queryset = CallTemplate.objects.all()
    serializer_class = CallTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="ponctuels")
    def ponctuels(self, request):
        """
        Retourne les templates ponctuels (sans offset_weeks ni recurrence_months).
        """
        qs = self.get_queryset().filter(
            offset_weeks__isnull=True,
            recurrence_months__isnull=True,
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
