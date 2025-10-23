from rest_framework import viewsets, permissions
from ..models import CallTemplate
from ..serializers import CallTemplateSerializer


class CallTemplateViewSet(viewsets.ModelViewSet):
    queryset = CallTemplate.objects.all()
    serializer_class = CallTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


