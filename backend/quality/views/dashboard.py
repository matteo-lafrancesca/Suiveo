from datetime import date, timedelta
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from ..models import Binome, Call
from ..serializers import CallSerializer, BinomeSerializer

class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet pour les KPIs et widgets du Dashboard.
    Ne gère pas de modèle unique, mais agrège des données.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def stats(self, request):
        today = date.today()
        # Calcul du début (Lundi) et fin (Dimanche) de la semaine courante
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)

        # 1. Compteurs KPI
        # ----------------
        active_binomes_count = Binome.objects.count()
        
        # En retard : Binômes flagués "En retard"
        retard_count = Binome.objects.filter(state=Binome.BinomeState.EN_RETARD).count()
        
        # Non conformes
        non_conforme_count = Binome.objects.filter(state=Binome.BinomeState.NON_CONFORME).count()
        
        # Appels de la SEMAINE (planifiés cette semaine et non réalisés)
        calls_week_count = Call.objects.filter(
            scheduled_date__range=[start_week, end_week], 
            actual_date__isnull=True
        ).count()

        # 2. Listes de widgets
        # --------------------
        # Top 5 des appels en retard (Date < start_week ET non réalisé)
        # On considère "En retard" tout ce qui est avant cette semaine courante
        # OU on garde la logique stricte "avant aujourd'hui" ? 
        # L'utilisateur dit "ça change seulement de semaine".
        # Donc un appel prévu Lundi, si on est Mardi et qu'il n'est pas fait, il est técniquement en retard 
        # mais il est aussi "dans la semaine".
        # Pour éviter les doublons entre "En retard" et "Appels de la semaine", on va dire :
        # Retard = Strictement avant le début de la semaine courante ?
        # Ou Retard = Strictement avant aujourd'hui ?
        # Restons sur "Retard = Avant aujourd'hui" pour l'urgence, 
        # et "Semaine" = "Tout ce qui est prévu cette semaine (y compris ce qui était hier Lundi et pas fait)".
        
        calls_retard_qs = Call.objects.filter(
            scheduled_date__lt=today, # On garde la notion de retard journalier pour l'alerte
            actual_date__isnull=True
        ).select_related('binome', 'binome__client', 'binome__employee', 'template').order_by('scheduled_date')[:5]

        # Liste des appels de la semaine
        calls_week_qs = Call.objects.filter(
            scheduled_date__range=[start_week, end_week],
            actual_date__isnull=True
        ).select_related('binome', 'binome__client', 'binome__employee', 'template').order_by('scheduled_date')

        return Response({
            "kpis": {
                "active_binomes": active_binomes_count,
                "retard": retard_count,
                "non_conforme": non_conforme_count,
                "calls_week": calls_week_count, # Renommé
            },
            "widgets": {
                "calls_retard": CallSerializer(calls_retard_qs, many=True).data,
                "calls_week": CallSerializer(calls_week_qs, many=True).data, # Renommé
            }
        })
