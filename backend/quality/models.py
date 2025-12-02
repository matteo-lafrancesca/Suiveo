from django.db import models


# --- Référentiels simples -----------------------------------------------------

class Client(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name}".strip()


class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name}".strip()


# --- Noyau métier -------------------------------------------------------------

class Binome(models.Model):
    """
    Lien entre un client & un intervenant, avec un état et des métadonnées.
    """

class Binome(models.Model):
    """
    Lien entre un client & un intervenant, avec un état et des métadonnées.
    """

    class BinomeState(models.TextChoices):
        CONFORME = "Conforme", "Conforme"
        NON_CONFORME = "Non conforme", "Non conforme"
        A_APPELER = "À appeler", "À appeler"
        EN_RETARD = "En retard", "En retard"

    class Rhythm(models.IntegerChoices):
        HEBDOMADAIRE = 1, "Hebdomadaire (Standard)"
        BIMENSUEL = 2, "Bimensuel (x2)"
        MENSUEL = 4, "Mensuel (x4)"

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="binomes")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="binomes")

    state = models.CharField(
        max_length=20,
        choices=BinomeState.choices,
        default=BinomeState.A_APPELER
    )

    rhythm = models.IntegerField(
        choices=Rhythm.choices,
        default=Rhythm.HEBDOMADAIRE,
        verbose_name="Rythme d'intervention"
    )

    first_intervention_date = models.DateField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Binôme"
        verbose_name_plural = "Binômes"
        unique_together = (("client", "employee"),)
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.client} × {self.employee} — {self.state}"


class BinomePause(models.Model):
    """
    Période de pause d'un binôme (ex. suspension de prestation).
    """
    binome = models.ForeignKey(Binome, on_delete=models.CASCADE, related_name="pauses")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    duration_days = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Pause de binôme"
        verbose_name_plural = "Pauses de binôme"
        ordering = ["-start_date"]

    def __str__(self):
        return f"Pause {self.binome} du {self.start_date} au {self.end_date or '…'}"


# --- Templates de récurrence --------------------------------------------------

class CallTemplate(models.Model):
    """
    Modèle de programmation d'appels : offset en semaines et récurrence en mois.
    """
    class CallType(models.TextChoices):
        CLIENT = "Client", "Client"
        EMPLOYEE = "Employé", "Employé"
        VISITE = "Visite", "Visite"
        RDV = "RDV" , "RDV"

    name = models.CharField(max_length=100, unique=True)
    offset_weeks = models.IntegerField(null=True, blank=True)
    recurrence_months = models.IntegerField(null=True, blank=True)
    type = models.CharField(
        max_length=20,
        choices=CallType.choices,
        default=CallType.CLIENT
    )

    class Meta:
        verbose_name = "Template d'appel"
        verbose_name_plural = "Templates d'appel"
        ordering = ["name"]

    def __str__(self):
        return self.name


# --- Événements planifiés / réalisés -----------------------------------------

class Call(models.Model):
    """
    Appels de suivi.
    """
    binome = models.ForeignKey(Binome, on_delete=models.CASCADE, related_name="calls")
    template = models.ForeignKey(CallTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name="calls")

    title = models.CharField(max_length=120)
    note = models.TextField(blank=True)
    report = models.TextField(null = True, blank=True)

    scheduled_date = models.DateField()
    actual_date    = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Appel"
        verbose_name_plural = "Appels"
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.title} — {self.binome}"
