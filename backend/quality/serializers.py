from datetime import date
from rest_framework import serializers
from .models import (
    Client, Employee, Binome, BinomePause,
    Call, CallTemplate
)
# 👇 Import du service métier
from .services.binome_service import BinomeService 

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

# --- Événements ---
class CallSerializer(serializers.ModelSerializer):
    template = CallTemplateSerializer(read_only=True)
    is_manual = serializers.SerializerMethodField()

    class Meta:
        model = Call
        fields = [
            "id", "title", "note", "report",
            "scheduled_date", "actual_date",
            "template", "is_manual",
        ]
    
    def get_is_manual(self, obj):
        """Un appel est manuel si son template n'a pas d'offset_weeks défini."""
        return obj.template.offset_weeks is None if obj.template else False

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
    
    rhythm_display = serializers.CharField(source='get_rhythm_display', read_only=True)
    next_call = serializers.SerializerMethodField()

    class Meta:
        model = Binome
        fields = [
            "id", "client", "employee",
            "client_id", "employee_id",
            "state", 
            "rhythm",          
            "rhythm_display", 
            "first_intervention_date",
            "note", "created_at",
            "next_call",
        ]

    def get_next_call(self, obj):
        # ✅ Utilisation du Service
        # On désactive l'auto-update pour ne pas ralentir la lecture (GET)
        service = BinomeService(obj, auto_update=False)
        call = service.get_next_call()
        
        return CallSerializer(call).data if call else None

class BinomePauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BinomePause
        fields = "__all__"

class BinomeEnrichiSerializer(serializers.ModelSerializer):
    # Champs calculés
    client_name = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    client_initials = serializers.SerializerMethodField()
    employee_initials = serializers.SerializerMethodField()
    rhythm_display = serializers.SerializerMethodField()
    week_sort_key = serializers.SerializerMethodField()
    state_color = serializers.SerializerMethodField()
    
    next_call = serializers.SerializerMethodField()

    class Meta:
        model = Binome
        fields = [
            'id', 'client', 'employee', 'state', 'rhythm', 
            'next_call',
            'client_name', 'employee_name', 'client_initials', 'employee_initials',
            'rhythm_display', 'week_sort_key', 'state_color'
        ]

    def get_next_call(self, obj):
        # ✅ Utilisation du Service
        service = BinomeService(obj, auto_update=False)
        call = service.get_next_call()
        
        # Formatage spécifique pour la vue enrichie (JSON léger)
        if call:
            return {
                "id": call.id,
                "scheduled_date": call.scheduled_date,
                "week_number": call.scheduled_date.isocalendar()[1],
                "year": call.scheduled_date.year,
                "template_name": call.template.name if call.template else "—"
            }
        return None

    # --- LOGIQUES D'AFFICHAGE (Restent ici car purement cosmétiques) ---
    def get_client_name(self, obj):
        if not obj.client: return "Client Inconnu"
        return f"{obj.client.last_name.upper()} {obj.client.first_name}"

    def get_employee_name(self, obj):
        if not obj.employee: return "Non assigné"
        return f"{obj.employee.last_name.upper()} {obj.employee.first_name}"

    def get_client_initials(self, obj):
        if not obj.client: return "?"
        return f"{obj.client.first_name[0]}{obj.client.last_name[0]}".upper()

    def get_employee_initials(self, obj):
        if not obj.employee: return "?"
        return f"{obj.employee.first_name[0]}{obj.employee.last_name[0]}".upper()

    def get_rhythm_display(self, obj):
        mapping = {1: "Hebdomadaire", 2: "Bimensuel", 4: "Mensuel"}
        return mapping.get(obj.rhythm, "Non défini")

    def get_week_sort_key(self, obj):
        # Réutilise la méthode interne qui utilise maintenant le service
        next_c = self.get_next_call(obj) 
        if not next_c:
            return 999999
        
        year = next_c['year']
        week = next_c['week_number']
        return (year * 100) + week

    def get_state_color(self, obj):
        if not obj.state: return "grey"
        s = obj.state.lower()
        if "non" in s: return "error"
        if "conforme" in s: return "success"
        if "appeler" in s or "retard" in s: return "warning"
        return "grey"