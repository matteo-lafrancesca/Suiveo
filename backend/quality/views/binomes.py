# app/views/binomes/base.py
from datetime import date, timedelta, datetime
from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Binome, CallTemplate, Employee, ClientEmployeeHistory
from ..serializers import BinomeEnrichiSerializer, BinomeSerializer, CallSerializer
from ..services.binome_service import BinomeService
from ..services.pause_service import PauseService
from ..services.call_service import CallService


import locale

from rest_framework import viewsets, permissions, status

try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except:
    # Fallback pour Windows
    locale.setlocale(locale.LC_TIME, "fr_FR")


class BinomeViewSet(viewsets.ModelViewSet):
    """ViewSet unique pour toutes les actions liées aux binômes."""
    queryset = Binome.objects.all()
    serializer_class = BinomeSerializer
    permission_classes = [permissions.IsAuthenticated]

    # ============================================================
    # 🟢 CREATE
    # ============================================================
    def create(self, request, *args, **kwargs):
        try:
            binome = BinomeService.create_with_first_call(request.data)
            return Response(BinomeSerializer(binome).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ============================================================
    # 📋 LISTE ENRICHIE
    # ============================================================

    @action(detail=False, methods=["get"], url_path="enrichis")
    def enrichis(self, request):
        """
        Retourne la liste des binômes enrichie via le Serializer Intelligent.
        Plus besoin de boucle for manuelle ici !
        """
        # 1. On récupère les binômes avec les relations pour éviter les requêtes N+1
        queryset = Binome.objects.select_related("client", "employee").all()
        
        # 2. On laisse le Serializer faire tout le travail de calcul (noms, couleurs, tri...)
        serializer = BinomeEnrichiSerializer(queryset, many=True)
        
        # 3. On renvoie le résultat
        return Response(serializer.data)    
    
    # ============================================================
    # 🧭 TIMELINE
    # ============================================================
    @action(detail=True, methods=["get"], url_path="timeline")
    def timeline(self, request, pk=None):
        binome = self.get_object()
        service = BinomeService(binome)
        data = service.get_timeline()

        return Response({
            "binome": BinomeSerializer(binome).data,
            "calls": CallSerializer(data["calls"], many=True).data,
            "next_call": CallSerializer(data["next_call"]).data if data["next_call"] else None,
            "last_call": CallSerializer(data["last_call"]).data if data["last_call"] else None,
            "show_report": data["show_report"],
        })

    @action(detail=True, methods=["get"], url_path="details")
    def details(self, request, pk=None):
        """
        Retourne :
        - le binôme complet
        - la liste des appels terminés (chronologique)
        - le prochain appel à venir
        """
        try:
            binome = Binome.objects.select_related("client", "employee").get(pk=pk)
        except Binome.DoesNotExist:
            return Response({"error": "Binôme introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # ⚙️ Logique via le service
        service = BinomeService(binome)
        calls = service.get_calls()
        completed_calls = [c for c in calls if c.actual_date]
        pending_calls = [c for c in calls if not c.actual_date]
        next_call = service.get_next_call()

        return Response({
            "binome": BinomeSerializer(binome).data,
            "completed_calls": CallSerializer(completed_calls, many=True).data,
            "pending_calls": CallSerializer(pending_calls, many=True).data,
            "next_call": CallSerializer(next_call).data if next_call else None,
        })
    
    # ============================================================
    # 🔄 HISTORIQUE DES INTERVENANTS
    # ============================================================
    @action(detail=False, methods=["get"], url_path="previous-employees")
    def previous_employees(self, request):
        """
        Retourne la liste des anciens intervenants pour un client donné.
        Utilisé pour afficher les suggestions dans le modal de changement d'intervenant.
        Query param: client_id
        """
        from ..serializers import EmployeeSerializer
        
        client_id = request.query_params.get('client_id')
        if not client_id:
            return Response({"error": "client_id requis"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Récupérer les IDs des intervenants qui ont déjà travaillé avec ce client
        history = ClientEmployeeHistory.objects.filter(
            client_id=client_id
        ).select_related('employee').order_by('-ended_at')
        
        # Extraire les employés (éviter doublons)
        seen_ids = set()
        previous_employees = []
        for record in history:
            if record.employee.id not in seen_ids:
                seen_ids.add(record.employee.id)
                previous_employees.append(record.employee)
        
        return Response(EmployeeSerializer(previous_employees, many=True).data)
    
    # ============================================================
    # 🗓️ PLANNING HEBDOMADAIRE
    # ============================================================
    @action(detail=False, methods=["get"], url_path="planning")
    def planning(self, request):
        """Retourne le planning hebdomadaire (basé sur le service)."""
        week = int(request.query_params.get("week", 0))
        year = int(request.query_params.get("year", timezone.now().year))

        data = BinomeService.get_week_planning(week if week else None, year)

        formatted_days = []
        for d in data["days"]:
            formatted_days.append({
                "date": d["date"].strftime("%Y-%m-%d"),
                "label": d["label"],
                "binomes": [
                    {
                        **BinomeSerializer(entry["binome"]).data,
                        "client_name": f"{entry['binome'].client.first_name} {entry['binome'].client.last_name}",
                        "employee_name": f"{entry['binome'].employee.first_name} {entry['binome'].employee.last_name}",
                        "next_call": {
                            "template_name": entry["call"].template.name if entry["call"].template else "—",
                            "template_type": entry["call"].template.type if entry["call"].template else None,
                            "scheduled_date": entry["call"].scheduled_date.strftime("%Y-%m-%d"),
                        }
                    }
                    for entry in d["binomes"]
                ]
            })

        return Response({
            "week_number": data["week_number"],
            "year": data["year"],
            "monday": data["monday"].strftime("%Y-%m-%d"),
            "friday": data["friday"].strftime("%Y-%m-%d"),
            "days": formatted_days,
        })
    # ============================================================
    # 📊 TABLEAU DE SUIVI
    # ============================================================
    @action(detail=False, methods=["get"], url_path="tableau-suivi")
    def tableau_suivi(self, request):
        """Retourne les binômes triés par état."""
        BinomeService.update_all_states()
        grouped = {
            "en_retard": [],
            "a_appeler": [],
            "non_conformes": [],
        }

        for b in Binome.objects.select_related("client", "employee"):
            service = BinomeService(b)
            next_call = service.get_next_call()

            serialized = BinomeSerializer(b).data
            serialized["client_name"] = f"{b.client.first_name} {b.client.last_name}"
            serialized["employee_name"] = f"{b.employee.first_name} {b.employee.last_name}"

            serialized["next_call"] = (
                CallSerializer(next_call).data if next_call else None
            )

            key = {
                "En retard": "en_retard",
                "À appeler": "a_appeler",
                "Non conforme": "non_conformes",
            }.get(b.state)

            if key:
                grouped[key].append(serialized)

        return Response(grouped)
    
    # ============================================================
    # 📞 GESTION APPELS MANUELS
    # ============================================================

    @action(detail=False, methods=["get"], url_path="manual-templates")
    def manual_templates(self, request):
        """
        Renvoie uniquement les templates 'neutres' (sans automatisme).
        On exclut ceux qui ont des règles de calcul (offset ou récurrence)
        pour éviter de casser le cycle automatique.
        """
        templates = CallTemplate.objects.filter(
            offset_weeks__isnull=True,
            recurrence_months__isnull=True
        ).order_by('name')

        data = [{"id": t.id, "name": t.name, "type": t.type} for t in templates]
        return Response(data)

    @action(detail=True, methods=["post"], url_path="schedule-manual")
    def schedule_manual(self, request, pk=None):
        """Crée un appel manuel sans perturber le cycle auto."""
        binome = self.get_object()
        
        template_id = request.data.get("template_id")
        date_str = request.data.get("date")
        title = request.data.get("title")

        if not template_id or not date_str:
            return Response(
                {"error": "Template et date sont obligatoires."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            CallService.create_manual_call(
                binome=binome,
                template_id=template_id,
                scheduled_date=date_str,
                title=title
            )
            # On force la mise à jour de l'état seulement si pas "Non conforme"
            # (sinon on sort de la non-conformité sans validation explicite)
            if binome.state != "Non conforme":
                BinomeService(binome).update_state()
            
            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST) 
        
        
    # ============================================================
    # ⏸️ GESTION PAUSES
    # ============================================================

    @action(detail=True, methods=["post"], url_path="schedule-pause")
    def schedule_pause(self, request, pk=None):
        """Programme une pause et décale le planning."""
        binome = self.get_object()
        start_date_str = request.data.get("start_date")
        end_date_str = request.data.get("end_date")

        if not start_date_str or not end_date_str:
            return Response(
                {"error": "Les dates de début et de fin sont requises."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Conversion des chaînes en objets date
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            service = PauseService(binome)
            service.create_pause(start_date, end_date)

            return Response({"status": "success"}, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log l'erreur réelle en console pour le débug
            print(f"Erreur schedule_pause: {e}")
            return Response({"error": "Erreur interne lors de la création de la pause."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
   
    # ============================================================
    # 🔄 CHANGEMENT D'INTERVENANT
    # ============================================================

    @action(detail=True, methods=["get"], url_path="available-employees")
    def available_employees(self, request, pk=None):
        """
        Retourne la liste des employés qui ne sont PAS déjà en binôme avec ce client.
        (Même si on supprime l'actuel juste après, c'est mieux de filtrer).
        """
        binome = self.get_object()
        client_id = binome.client.id
        
        # On exclut les employés qui ont déjà un binôme avec ce client (sauf l'actuel, mais on va le changer)
        # Dans la logique stricte : on veut tous les employés sauf celui du binôme actuel 
        # (et éventuellement d'autres si le client a plusieurs binômes, ce qui est rare mais possible).
        
        busy_employees_ids = Binome.objects.filter(client_id=client_id).values_list('employee_id', flat=True)
        
        # On veut tous les employés SAUF ceux déjà liés au client
        available = Employee.objects.exclude(id__in=busy_employees_ids).order_by('last_name', 'first_name')
        
        data = [{"id": e.id, "name": f"{e.first_name} {e.last_name}"} for e in available]
        return Response(data)

    @action(detail=True, methods=["post"], url_path="change-employee")
    def change_employee(self, request, pk=None):
        old_binome = self.get_object()
        
        new_employee_id = request.data.get("employee_id")
        new_start_date_str = request.data.get("start_date")
        # On récupère le rythme (ou on garde l'ancien)
        new_rhythm = request.data.get("rhythm", old_binome.rhythm)
        
        # 👇 AJOUT : On récupère la note
        # Si "note" est dans la requête, on l'utilise. Sinon, on garde l'ancienne.
        new_note = request.data.get("note", old_binome.note)

        if not new_employee_id or not new_start_date_str:
            return Response({"error": "Intervenant et date de début requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                client_id = old_binome.client.id
                old_employee_id = old_binome.employee.id
                
                # 📝 Enregistrer l'historique de l'ancien intervenant
                ClientEmployeeHistory.objects.create(
                    client_id=client_id,
                    employee_id=old_employee_id,
                    ended_at=timezone.now()
                )
                
                old_binome.delete()

                new_data = {
                    "client_id": client_id,
                    "employee_id": new_employee_id,
                    "first_intervention_date": new_start_date_str,
                    "rhythm": int(new_rhythm),
                    "note": new_note  # 👈 On injecte la note ici
                }
                
                new_binome = BinomeService.create_with_first_call(new_data)
                
                return Response({
                    "status": "success", 
                    "new_binome_id": new_binome.id
                }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Erreur changement intervenant: {e}")
            return Response({"error": "Erreur interne."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get_serializer_class(self):
        if self.action == 'list':
            return BinomeEnrichiSerializer
        return BinomeSerializer