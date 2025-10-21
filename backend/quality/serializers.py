from datetime import date
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


# --- Templates ---
class CallTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallTemplate
        fields = ["id", "name", "type"]


class FieldVisitTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldVisitTemplate
        fields = "__all__"


# --- Événements ---
class CallSerializer(serializers.ModelSerializer):
    # 🔹 Inclure le template complet (type, id, name)
    template = CallTemplateSerializer(read_only=True)

    class Meta:
        model = Call
        fields = [
            "id", "title", "note",
            "scheduled_date", "actual_date",
            "template",
        ]


class FieldVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldVisit
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

    # ➕ Ajout du champ calculé
    next_call = serializers.SerializerMethodField()

    class Meta:
        model = Binome
        fields = [
            "id", "client", "employee",
            "client_id", "employee_id",
            "state", "first_intervention_date",
            "note", "created_at",
            "next_call",
        ]

    def get_next_call(self, obj):
        today = date.today()

        # 1️⃣ Appel en retard (non fait et date passée)
        call = (
            Call.objects
            .filter(
                binome=obj,
                actual_date__isnull=True,
                scheduled_date__lt=today
            )
            .order_by("scheduled_date")
            .select_related("template")
            .first()
        )

        # 2️⃣ Sinon prochain appel futur
        if not call:
            call = (
                Call.objects
                .filter(
                    binome=obj,
                    scheduled_date__gte=today
                )
                .order_by("scheduled_date")
                .select_related("template")
                .first()
            )

        return CallSerializer(call).data if call else None


class BinomePauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BinomePause
        fields = "__all__"
