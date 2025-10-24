# app/views/binomes/base.py
from datetime import date, timedelta

from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Binome
from ..serializers import BinomeSerializer, CallSerializer
from ..services.binome_service import BinomeService

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
        """Retourne la liste des binômes enrichie (format plat pour le front)."""
        enriched = BinomeService.get_all_enriched()
        data = []

        for e in enriched:
            binome = e["binome"]
            last_call = e["last_call"]
            next_call = e["next_call"]

            serialized = BinomeSerializer(binome).data

            # Dernier appel (si existant)
            serialized["last_call"] = (
                {
                    "template_name": last_call.template.name if last_call and last_call.template else "—",
                    "actual_date": last_call.actual_date if last_call else None,
                }
                if last_call
                else None
            )

            # Prochain appel (si existant)
            serialized["next_call"] = (
                {
                    "template_name": next_call.template.name if next_call and next_call.template else "—",
                    "template_type": next_call.template.type if next_call and next_call.template else None,
                    "scheduled_date": next_call.scheduled_date if next_call else None,
                    "week_number": (
                        next_call.scheduled_date.isocalendar()[1]
                        if next_call and next_call.scheduled_date
                        else None
                    ),
                }
                if next_call
                else None
            )

            data.append(serialized)

        return Response(data)
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
        next_call = service.get_next_call()

        return Response({
            "binome": BinomeSerializer(binome).data,
            "completed_calls": CallSerializer(completed_calls, many=True).data,
            "next_call": CallSerializer(next_call).data if next_call else None,
        })
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
