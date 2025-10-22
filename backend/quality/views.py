from datetime import timedelta
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    Client,
    Employee,
    Binome,
    Call,
    CallTemplate,
    FieldVisit,
    FieldVisitTemplate,
)
from .serializers import (
    ClientSerializer,
    EmployeeSerializer,
    BinomeSerializer,
    CallSerializer,
    CallTemplateSerializer,
    FieldVisitSerializer,
    FieldVisitTemplateSerializer,
)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="disponibles")
    def disponibles(self, request):
        clients_avec_binome = Binome.objects.values_list("client_id", flat=True)
        clients_libres = Client.objects.exclude(id__in=clients_avec_binome)
        serializer = ClientSerializer(clients_libres, many=True)
        return Response(serializer.data)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]


class BinomeViewSet(viewsets.ModelViewSet):
    queryset = Binome.objects.all()
    serializer_class = BinomeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """⚙️ Surcharge pour afficher les erreurs du serializer dans la console"""
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("❌ Erreur de validation du serializer Binome :")
            for field, errors in serializer.errors.items():
                print(f" - {field}: {errors}")
            return Response(serializer.errors, status=400)

        # ✅ Si OK, on crée le binôme normalement
        binome = serializer.save()

        try:
            templates = CallTemplate.objects.all()

            for template in templates:
                scheduled_date = binome.first_intervention_date + timedelta(weeks=template.offset_weeks)
                title = f"{template.name} du {scheduled_date.strftime('%d/%m/%Y')}"
                Call.objects.create(
                    binome=binome,
                    template=template,
                    title=title,
                    scheduled_date=scheduled_date,
                )

            print(f"✅ {len(templates)} appels créés pour le binôme {binome}")

        except Exception as e:
            import traceback
            print("❌ ERREUR lors de la création automatique des appels :")
            traceback.print_exc()
            raise e

        return Response(serializer.data, status=201)

class CallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all()
    serializer_class = CallSerializer
    permission_classes = [permissions.IsAuthenticated]


class CallTemplateViewSet(viewsets.ModelViewSet):
    queryset = CallTemplate.objects.all()
    serializer_class = CallTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class FieldVisitViewSet(viewsets.ModelViewSet):
    queryset = FieldVisit.objects.all()
    serializer_class = FieldVisitSerializer
    permission_classes = [permissions.IsAuthenticated]


class FieldVisitTemplateViewSet(viewsets.ModelViewSet):
    queryset = FieldVisitTemplate.objects.all()
    serializer_class = FieldVisitTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
