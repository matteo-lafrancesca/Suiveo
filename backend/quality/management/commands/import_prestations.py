import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from quality.models import Client, Employee, Binome

class Command(BaseCommand):
    help = 'Import clients and employees from CSV file (resetting DB)'

    def handle(self, *args, **options):
        csv_path = os.path.join(settings.BASE_DIR, 'export prestations.csv')

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'File not found: {csv_path}'))
            return

        self.stdout.write(self.style.WARNING('⚠️  Resetting database (Clients, Employees)...'))
        
        with transaction.atomic():
            # 1. Nettoyage
            # La suppression des Clients/Employés entraîne la suppression des Binômes (CASCADE)
            Client.objects.all().delete()
            Employee.objects.all().delete()
            
            self.stdout.write(self.style.SUCCESS('✅ Database cleared.'))

            # 2. Lecture et Déduplication
            unique_clients = set()
            unique_employees = set()

            # Essai avec utf-8-sig pour gérer le BOM Excel éventuel
            try:
                f = open(csv_path, 'r', encoding='utf-8-sig')
                reader = csv.DictReader(f, delimiter=';')
            except UnicodeDecodeError:
                f = open(csv_path, 'r', encoding='cp1252')
                reader = csv.DictReader(f, delimiter=';')

            # Debug headers
            self.stdout.write(f"Headers trouvés : {reader.fieldnames}")

            for row in reader:
                # On essaie de récupérer avec strip() pour être sûr
                # On nettoie les clés du dictionnaire pour enlever les espaces potentiels
                clean_row = {k.strip(): v for k, v in row.items() if k}
                
                client_raw = clean_row.get('Nom prénom client', '').strip()
                employee_raw = clean_row.get("Nom de l'employé", '').strip()
                
                if client_raw:
                    unique_clients.add(client_raw)
                if employee_raw:
                    unique_employees.add(employee_raw)
            
            f.close()

            self.stdout.write(self.style.MIGRATE_HEADING(f'Trouvé {len(unique_clients)} clients uniques et {len(unique_employees)} employés uniques dans le CSV.'))

            # 3. Création des Clients
            created_clients = 0
            for raw_name in unique_clients:
                last_name, first_name = self.parse_name(raw_name)
                Client.objects.create(first_name=first_name, last_name=last_name)
                created_clients += 1
            
            self.stdout.write(self.style.SUCCESS(f'--> {created_clients} Clients créés.'))

            # 4. Création des Employés
            created_employees = 0
            for raw_name in unique_employees:
                last_name, first_name = self.parse_name(raw_name)
                Employee.objects.create(first_name=first_name, last_name=last_name)
                created_employees += 1

            self.stdout.write(self.style.SUCCESS(f'--> {created_employees} Employés créés.'))
            self.stdout.write(self.style.SUCCESS('🎉 Import terminé avec succès.'))

    def parse_name(self, raw_str):
        """
        Parse une chaîne type "NOM Prénom [ID]"
        Heuristique : Les mots en MAJUSCULES sont le Nom, les autres le Prénom.
        """
        # On enlève la partie [ID]
        name_part = raw_str.split('[')[0].strip()
        
        parts = name_part.split()
        last_name_parts = []
        first_name_parts = []
        
        for part in parts:
            # On considère comme nom de famille si tout en majuscule
            # et contient au moins une lettre (pour éviter les cas bizarres)
            if part.isupper() and any(c.isalpha() for c in part):
                last_name_parts.append(part)
            else:
                first_name_parts.append(part)
        
        # Fallback si tout est majuscule ou tout minuscule
        if not last_name_parts and parts:
             # Si échec heuristique, on prend le premier mot comme NOM par défaut
             last_name_parts.append(parts[0])
             first_name_parts = parts[1:]

        return " ".join(last_name_parts), " ".join(first_name_parts)
