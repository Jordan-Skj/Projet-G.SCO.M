from django.conf import settings 
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

class Auditlog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'create', 'Création'
        UPDATE = 'update', 'Modification'
        VERIFY = 'verify', 'Vérification'
        REJECT = 'reject', 'Rejet'
        VOID = 'void', 'Annulation'
        AUTHORIZE_RETURN = 'authorize_return', 'Autorisation de retour en classe'

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='audit_logs', verbose_name='Auteur de l\'action')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date et heure de l\'action')
    action = models.CharField(max_length=20, choices=Action.choices, verbose_name='Action')
    target_type = models.CharField(max_length=100, verbose_name="Type d'objet", help_text="Ex : finance.feepayment")
    target_id = models.CharField(max_length=50, verbose_name="Identifiant de l'objet")
    target_repr = models.CharField(max_length=255, verbose_name="Description de l'objet")
    before = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder, verkbose_name="Valeurs avant")
    after = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder, verbose_name="Valeurs apres")
    reason = models.TextField(blank=True, verbose_name="Motif")

    class Meta:
        ordering = ['-created_at', '-id']
        default_permissions = ('view', )
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journal d'audit"
        indexes = [
            models.Index(fields=['target_type', 'target_id']),
        ]
        
    def save(self, *args : object, **kwargs : object) -> None:
        if not self._state.adding:
            raise PermissionDenied("In journal d'audit ne peut pas être modifié.")
        super().save(*args, **kwargs)
        
    def delete(self, *args : object, **kwargs) -> None:
        raise PermissionDenied("Un journal d'audit ne peut pas être supprimé.")
    
    def __str__(self) -> str:   
        return f"{self.created_at:%Y-%m-%d %H:%M} | {self.actor} | {self.action} | {self.target_repr}"