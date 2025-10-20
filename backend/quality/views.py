from rest_framework import viewsets, permissions
from .models import (
    Client, Employee, Binome,
    Call, CallTemplate, FieldVisit, FieldVisitTemplate
)
from .serializers import (
    ClientSerializer, EmployeeSerializer, BinomeSerializer,
    CallSerializer, CallTemplateSerializer, FieldVisitSerializer, FieldVisitTemplateSerializer
)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]


class BinomeViewSet(viewsets.ModelViewSet):
    queryset = Binome.objects.all()
    serializer_class = BinomeSerializer
    permission_classes = [permissions.IsAuthenticated]

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
