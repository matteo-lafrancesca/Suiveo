from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Supprime les utilisateurs invités (sans mot de passe défini) créés il y a plus de 30 minutes.'

    def handle(self, *args, **options):
        threshold_time = timezone.now() - timedelta(minutes=30)
        
        # On cible les utilisateurs invités qui n'ont jamais défini de mot de passe
        # (is_active=False ET password vide/unusable ET créés avant le seuil)
        expired_users = User.objects.filter(
            is_active=False,
            role=User.Role.SUPERVISOR,
            date_joined__lt=threshold_time
        )
        
        # Filtrer ceux qui n'ont pas de mot de passe utilisable
        expired_users = [u for u in expired_users if not u.has_usable_password()]
        count = len(expired_users)
        
        if count > 0:
            self.stdout.write(self.style.WARNING(f'Suppression de {count} utilisateur(s) invité(s) sans mot de passe...'))
            for user in expired_users:
                user.delete()
            self.stdout.write(self.style.SUCCESS(f'{count} utilisateur(s) supprimé(s) avec succès.'))
        else:
            self.stdout.write(self.style.SUCCESS('Aucun utilisateur invité sans mot de passe à supprimer.'))
