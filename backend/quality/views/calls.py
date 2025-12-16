# app/views/calls.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.core.exceptions import ValidationError
from ..models import Call
from ..serializers import CallSerializer
from ..services.call_service import CallService
from ..services.pause_service import PauseService
from ..services.binome_service import BinomeService


class CallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all().select_related("template", "binome")
    serializer_class = CallSerializer
    permission_classes = [permissions.IsAuthenticated]

    # ============================================================
    # 🔄 Reprogrammer un appel
    # ============================================================
    @action(detail=True, methods=["post"], url_path="reprogrammer")
    def reprogrammer(self, request, pk=None):
        call = self.get_object()
        new_date = request.data.get("new_date")
        if not new_date:
            return Response({"error": "Nouvelle date requise"}, status=400)

        call.scheduled_date = new_date
        call.title = f"{call.template.name} du {new_date}"
        call.save(update_fields=["scheduled_date", "title"])

        return Response({"success": True, "call": CallSerializer(call).data})

    # ============================================================
    # ✅ Marquer comme conforme
    # ============================================================
    @action(detail=True, methods=["post"], url_path="conforme")
    def conforme(self, request, pk=None):
        call = self.get_object()
        service = CallService(call)
        next_call = service.mark_conforme(note=request.data.get("note", ""))

        # 🔹 Recharge le binôme depuis la base pour être sûr d’avoir le state à jour
        call.binome.refresh_from_db()

        return Response({
            "success": True,
            "message": "Appel marqué comme conforme.",
            "next_call": CallSerializer(next_call).data if next_call else None,
            "report": call.report,
            "binome_state": call.binome.state,
        })

    # ============================================================
    # ❌ Marquer comme non conforme
    # ============================================================
    @action(detail=True, methods=["post"], url_path="non-conforme")
    def non_conforme(self, request, pk=None):
        call = self.get_object()
        service = CallService(call)
        service.mark_non_conforme()

        return Response({
            "success": True,
            "message": "Binôme marqué comme non conforme et pause créée.",
            "report": call.report,
        })
    @action(detail=True, methods=["post"], url_path="reprogrammer")
    def reprogrammer(self, request, pk=None):
        call = self.get_object()
        new_date = request.data.get("new_date")
        reason = request.data.get("reason", "") # On récupère le motif

        if not new_date:
            return Response({"error": "Nouvelle date requise"}, status=400)

        # Utilisation du service pour la logique "Historique + Nouveau"
        service = CallService(call)
        new_call = service.reschedule_with_history(new_date, reason)

        return Response({
            "success": True, 
            "message": "Appel reprogrammé avec succès.",
            "new_call": CallSerializer(new_call).data
        })
    
    # ============================================================
    # 🔓 Rouvrir un appel terminé
    # ============================================================
    @action(detail=True, methods=["post"], url_path="reopen")
    def reopen(self, request, pk=None):
        """
        Rouvre un appel terminé en retirant actual_date et report.
        Si l'appel avait mis le binôme en Non conforme, annule la pause.
        Si l'appel précédent était Non conforme, restaure cet état.
        Supprime également l'appel suivant créé automatiquement.
        """
        call = self.get_object()
        
        if not call.actual_date:
            return Response(
                {"error": "Cet appel n'est pas terminé."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        binome = call.binome
        was_non_conforme_call = call.outcome == "Non conforme"
        
        # 1. Supprimer l'appel suivant créé automatiquement (s'il existe et n'est pas réalisé)
        if call.created_next_call and not call.created_next_call.actual_date:
            call.created_next_call.delete()
        
        # 2. Si c'était l'appel qui a mis en non-conformité, annuler la pause
        if was_non_conforme_call and binome.state == "Non conforme":
            pause_service = PauseService(binome)
            try:
                # Annuler la pause active
                active_pause = binome.pauses.filter(end_date__isnull=True).first()
                if active_pause:
                    active_pause.delete()
            except Exception:
                pass
        
        # 3. Réinitialiser l'appel
        call.actual_date = None
        call.report = ""
        call.note = ""
        call.outcome = None
        call.created_next_call = None
        call.save(update_fields=["actual_date", "report", "note", "outcome", "created_next_call"])
        
        # 4. Vérifier si l'appel précédent (via previous_call) était "Non conforme"
        # Utilisation de la chaîne chronologique en BDD au lieu des dates
        if call.previous_call and call.previous_call.outcome == "Non conforme":
            # Restaurer l'état "Non conforme"
            binome.state = "Non conforme"
            binome.save(update_fields=["state"])
            
            # Recréer la pause indéfinie
            try:
                pause_service = PauseService(binome)
                pause_service.start_pause(start_date=call.previous_call.actual_date)
            except ValidationError:
                pass  # Si pause existe déjà
        else:
            # Recalculer l'état du binôme normalement
            BinomeService(binome).update_state()
        
        binome.refresh_from_db()
        
        return Response({
            "success": True,
            "message": "Appel rouvert avec succès.",
            "binome_state": binome.state,
        })
    
    # ============================================================
    # 🗑️ Supprimer un appel manuel
    # ============================================================
    def destroy(self, request, *args, **kwargs):
        """
        Supprime un appel manuel non réalisé.
        Refuse de supprimer les appels automatiques ou déjà réalisés.
        """
        call = self.get_object()
        
        # Vérifier que l'appel n'est pas encore réalisé
        if call.actual_date:
            return Response(
                {"error": "Impossible de supprimer un appel déjà réalisé."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que c'est un appel manuel (pas d'offset_weeks ni recurrence_months)
        if call.template and (call.template.offset_weeks is not None or call.template.recurrence_months is not None):
            return Response(
                {"error": "Impossible de supprimer un appel automatique."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        call.delete()
        
        return Response({
            "success": True,
            "message": "Appel manuel supprimé avec succès.",
        }, status=status.HTTP_200_OK)