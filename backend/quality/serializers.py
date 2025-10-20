from rest_framework import serializers
from .models import (
    Client, Employee, Binome, BinomePause,
    Call, CallTemplate, FieldVisit, FieldVisitTemplate
)


# --- Référentiels ---
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"


# --- Noyau métier ---
class BinomeSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    employee = EmployeeSerializer(read_only=True)

    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(), source="client", write_only=True
    )
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), source="employee", write_only=True
    )

    class Meta:
        model = Binome
        fields = [
            "id", "client", "employee",
            "client_id", "employee_id",
            "state", "first_intervention_date",
            "note", "created_at"
        ]


class BinomePauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BinomePause
        fields = "__all__"


# --- Templates ---
class CallTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallTemplate
        fields = "__all__"


class FieldVisitTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldVisitTemplate
        fields = "__all__"


# --- Événements ---
class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = "__all__"


class FieldVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldVisit
        fields = "__all__"
