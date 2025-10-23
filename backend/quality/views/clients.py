from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Client, Binome
from ..serializers import ClientSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="disponibles")
    def disponibles(self, request):
        """Renvoie les clients sans binôme."""
        clients_avec_binome = Binome.objects.values_list("client_id", flat=True)
        clients_libres = Client.objects.exclude(id__in=clients_avec_binome)
        serializer = self.get_serializer(clients_libres, many=True)
        return Response(serializer.data)
