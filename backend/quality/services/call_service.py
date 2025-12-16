from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from ..models import Call, CallTemplate, Binome
from .pause_service import PauseService

class CallService:
    """Service métier gérant la création et la planification des appels."""

    def __init__(self, call: Call):
        self.call = call
        self.binome = call.binome
        self.template = call.template
        self.pause_service = PauseService(self.binome)

    # ============================================================
    # 🛠️ UTILITAIRES STATIQUES
    # ============================================================
    @staticmethod
    def get_last_completed_call(binome: Binome):
        """Récupère le dernier appel réalisé (avec date réelle)."""
        return Call.objects.filter(binome=binome, actual_date__isnull=False).order_by("-actual_date").first()

    # NOTE: Cette méthode n'est plus utilisée. Les appels sont maintenant décalés au lieu d'être supprimés.
    # Conservée pour usage manuel si nécessaire.
    @staticmethod
    def remove_future_pending_calls(binome: Binome):
        """[DEPRECATED] Supprime les appels prévus mais non réalisés."""
        Call.objects.filter(binome=binome, actual_date__isnull=True).delete()

    @staticmethod
    def schedule_first_call(binome: Binome):
        """
        Logique centralisée pour créer le TOUT premier appel.
        ⚠️ Le premier appel est TOUJOURS à 1 semaine (+1 jour), peu importe le rythme.
        Le rythme (bimensuel/mensuel) ne s'applique qu'à partir du 2ème appel.
        """
        first_template = CallTemplate.objects.filter(offset_weeks__isnull=False).order_by("offset_weeks").first()
        
        if not first_template:
            return None

        # Calcul du décalage dû aux pauses éventuelles
        pause_delay = PauseService(binome).get_total_delay()
        
        # ⚠️ PREMIER APPEL : toujours à offset_weeks de base (pas de multiplication par rhythm)
        # Le rythme s'applique uniquement aux appels suivants
        adjusted_offset_weeks = first_template.offset_weeks  # Pas de multiplication ici

        # Date = Début prestation + 1 jour (appels le lendemain) + Offset de base + Pauses
        reference_date = binome.first_intervention_date + timedelta(days=1)
        
        # Si le lendemain tombe un samedi (5) ou dimanche (6), décaler au lundi
        if reference_date.weekday() == 5:  # Samedi
            reference_date += timedelta(days=2)  # Passer à lundi
        elif reference_date.weekday() == 6:  # Dimanche
            reference_date += timedelta(days=1)  # Passer à lundi
        
        scheduled_date = reference_date + timedelta(weeks=adjusted_offset_weeks) + timedelta(days=pause_delay)

        return Call.objects.create(
            binome=binome,
            template=first_template,
            title=first_template.name,
            scheduled_date=scheduled_date,
            previous_call=None,  # Premier appel : pas de précédent
        )    
    
    # ============================================================
    # ➕ CRÉATION MANUELLE (NOUVEAU)
    # ============================================================
    @staticmethod
    def create_manual_call(binome, template_id, scheduled_date, title=None):
        template = CallTemplate.objects.get(pk=template_id)
        
        # Si aucun titre fourni, on prend le nom du template
        final_title = title or f"{template.name} (Manuel)"
        
        # Définir previous_call = dernier appel réalisé
        last_completed = CallService.get_last_completed_call(binome)
        
        return Call.objects.create(
            binome=binome,
            template=template,
            scheduled_date=scheduled_date,
            title=final_title,
            previous_call=last_completed,
        )


    # ============================================================
    # 🔁 PLANIFICATION AUTOMATIQUE
    # ============================================================
    def schedule_next_call(self):
        """Programme le prochain appel en tenant compte des pauses ET du rythme."""
        
        if self.pause_service.is_currently_paused():
            return None

        if not self.template:
            return None

        # --- 🛡️ GARDE-FOU 🛡️ ---
        if self.template.offset_weeks is None and self.template.recurrence_months is None:
            return None
        # ------------------------

        next_date = None
        next_template = None
        
        # 🔄 CAS 1 : Récurrence mensuelle (Logique long terme)
        # Note: Généralement la récurrence mensuelle (ex: point annuel) n'est pas affectée 
        # par le rythme opérationnel hebdo/bimensuel. On la laisse telle quelle.
        if self.template.recurrence_months:
            base_date = self.call.scheduled_date + relativedelta(months=self.template.recurrence_months)
            pause_delay = self.pause_service.get_total_delay(since_date=self.call.scheduled_date)
            
            next_date = base_date + timedelta(days=pause_delay)
            next_template = self.template

        else:
            next_template = (
                CallTemplate.objects
                .filter(offset_weeks__gt=self.template.offset_weeks)
                .order_by("offset_weeks")
                .first()
            )
            if not next_template:
                return None
            
            # ⚠️ Le premier appel (offset_weeks=1) ne doit jamais être multiplié par le rythme
            # Les appels suivants (offset_weeks > 1) sont multipliés par le rythme
            first_template = CallTemplate.objects.filter(offset_weeks__isnull=False).order_by("offset_weeks").first()
            is_scheduling_first_call = (first_template and next_template.id == first_template.id)
            
            if is_scheduling_first_call:
                # Premier appel : pas de multiplication par le rythme
                adjusted_offset_weeks = next_template.offset_weeks
            else:
                # Appels suivants : on applique le rythme
                adjusted_offset_weeks = next_template.offset_weeks * self.binome.rhythm

            # Date de référence = première intervention + 1 jour (appels le lendemain)
            reference_date = self.binome.first_intervention_date + timedelta(days=1)
            
            # Si le lendemain tombe un samedi (5) ou dimanche (6), décaler au lundi
            if reference_date.weekday() == 5:  # Samedi
                reference_date += timedelta(days=2)  # Passer à lundi
            elif reference_date.weekday() == 6:  # Dimanche
                reference_date += timedelta(days=1)  # Passer à lundi
            
            theoretical_date = reference_date + timedelta(weeks=adjusted_offset_weeks)
            total_pause_delay = self.pause_service.get_total_delay()
            
            next_date = theoretical_date + timedelta(days=total_pause_delay)

        if next_date and next_template:
            # Définir previous_call = dernier appel réalisé
            last_completed = CallService.get_last_completed_call(self.binome)
            
            return Call.objects.create(
                binome=self.binome,
                template=next_template,
                title=f"{next_template.name} du {next_date.strftime('%d/%m/%Y')}",
                scheduled_date=next_date,
                previous_call=last_completed,
            )
        return None
    
    # ============================================================
    # ✅ CONFORMITÉ / ❌ NON-CONFORMITÉ
    # ============================================================
    
    def _schedule_after_non_conformite(self) -> Call | None:
        """
        Programme le prochain appel automatique après une sortie de non-conformité.
        Pour les appels manuels, reprogramme depuis le dernier appel automatique.
        """
        # Si appel manuel (pas d'offset_weeks ni recurrence_months)
        if not self.template or (self.template.offset_weeks is None and self.template.recurrence_months is None):
            # Chercher le dernier appel automatique réalisé
            last_auto_call = CallService.get_last_completed_call(self.binome)
            if last_auto_call and last_auto_call.template and (last_auto_call.template.offset_weeks is not None or last_auto_call.template.recurrence_months is not None):
                return CallService(last_auto_call).schedule_next_call()
            else:
                # Pas d'appel auto trouvé, on crée le premier appel
                return CallService.schedule_first_call(self.binome)
        else:
            # Appel automatique : programmation normale
            return self.schedule_next_call()
    
    def mark_conforme(self, note: str = "") -> Call | None:
        self.call.note = note or "Le client est satisfait de la prestation."
        self.call.actual_date = timezone.now().date()
        self.call.outcome = "Conforme"

        # 🔹 Si le binôme était "Non conforme", on arrête la pause et on reprogramme
        was_non_conforme = self.binome.state == "Non conforme"
        
        if was_non_conforme:
            # Arrêter la pause (peut lever ValidationError si pas de pause active)
            try:
                self.pause_service.stop_pause()
            except Exception as e:
                # Si pas de pause active, continuer quand même
                pass
            
            self.binome.refresh_from_db()
            
            # 🔓 Forcer la sortie de "Non conforme"
            self.binome.state = "Conforme"
            self.binome.save(update_fields=["state"])
            
            # Programmer le prochain appel (logique centralisée)
            new_call = self._schedule_after_non_conformite()
        else:
            # Cas normal (pas de non-conformité)
            new_call = self.schedule_next_call()

        # Stocker la référence de l'appel créé
        if new_call:
            self.call.created_next_call = new_call
            next_str = new_call.scheduled_date.strftime("%d/%m/%Y")
            self.call.report = f"✅ Binôme conforme — appel suivant programmé le {next_str}."
        elif self.pause_service.is_currently_paused():
            self.call.report = "⏸️ Binôme en pause — planification suspendue."
        else:
            self.call.report = "✅ Binôme conforme — aucun autre appel à programmer."

        self.call.save(update_fields=["note", "actual_date", "report", "outcome", "created_next_call"])
        
        # Mise à jour état binôme (affinera l'état selon le prochain appel)
        from .binome_service import BinomeService
        BinomeService(self.binome).update_state()
        
        return new_call

    def mark_non_conforme(self):
        # 1. Mettre à jour l'appel
        self.call.actual_date = timezone.now().date()
        self.call.outcome = "Non conforme"
        self.call.report = (
            "⛔ Binôme non conforme — Action corrective requise. "
        )
        self.call.save(update_fields=["actual_date", "report", "outcome"])

        # 2. Créer la pause indéfinie (les appels futurs seront décalés lors de stop_pause)
        self.pause_service.start_pause()

        # 3. Forcer l'état
        self.binome.state = "Non conforme"
        self.binome.save(update_fields=["state"])

    def reschedule_with_history(self, new_date, reason):
        """
        Marque l'appel actuel comme "Tentative" et crée un clone pour la nouvelle date.
        """
        # 1. On archive la tentative actuelle
        self.call.actual_date = timezone.now().date()
        self.call.outcome = "Reprogrammé"
        
        # --- CORRECTION FORMAT DATE ---
        # Si c'est une chaîne (ex: "2025-12-03"), on la convertit d'abord
        if isinstance(new_date, str):
            date_obj = datetime.strptime(new_date, "%Y-%m-%d").date()
            formatted_date = date_obj.strftime('%d/%m/%Y')
        else:
            # Si c'est déjà un objet date
            formatted_date = new_date.strftime('%d/%m/%Y')
        # ------------------------------

        self.call.report = f"⚠️ Reprogrammé (Relance prévue le {formatted_date})"
        
        if reason:
            self.call.note = reason 
            self.call.report += f" — Motif : {reason}"
            
        self.call.save(update_fields=["actual_date", "report", "note", "outcome"])

        # 2. On crée le nouvel appel (Retry)
        new_call = Call.objects.create(
            binome=self.binome,
            template=self.call.template,
            title=self.call.template.name, # Nom propre (sans date)
            scheduled_date=new_date
        )
        
        return new_call