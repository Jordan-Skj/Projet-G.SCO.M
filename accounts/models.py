from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        DIRECTOR = 'director', 'Directeur'
        SECRETARY = 'secretary', 'Secrétaire'
        TEACHER = 'teacher', 'Enseignant'
        ACCOUNTANT = 'accountant', 'Comptable'
        PARENT = 'parent', 'Parent'
        GUARD = 'guard', 'Garde'
        PREFECT = 'prefect', 'Préfet'
        INSEPECTOR = 'inspector', 'Inspecteur'
        ADMIN = 'admin', 'Administrateur'
        
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PARENT, verbose_name='Rôle')
    REQUIRED_FIELDS : list[str] = AbstractUser.REQUIRED_FIELDS + ['role']
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        
    def __str__(self) -> str:
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

# The parent model
class Parent(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="parent_profile")
    phone_number = models.CharField(max_length=20, verbose_name="Numéro de téléphone")
    alternate_phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numéro de téléphone alternatif")
    address = models.TextField(verbose_name="Adresse")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")
    
    
    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents"
        
    def __str__(self) -> str:
        return f"Parent {self.user.get_username()} | {self.phone_number}"
