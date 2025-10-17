from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager  # ✅ importer ton manager

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "Admin", "Admin"
        SUPERVISOR = "Supervisor", "Supervisor"

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SUPERVISOR)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Pas de champs supplémentaires obligatoires

    objects = UserManager()  # ✅ on définit notre manager

    def __str__(self):
        return f"{self.email} ({self.role})"
