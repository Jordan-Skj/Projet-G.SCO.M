from django.db import models
from Gscom import settings
from students.models import Enrollment

class Punishment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Sanction à executer'
        IN_PROGRESS = 'in_progress', 'Sanction en cours'
        COMPLETED = 'completed', 'Sanction exécutée'
        CANCELED = 'canceled', 'Sanction annulée'
        
    violated_article = models.CharField(max_length=255, verbose_name="Article du reglement scolaire violé")
    description = models.TextField(verbose_name="Description de la punition")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    punished_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='issued_punishments', verbose_name="Sanctionné par")
    sanction = models.TextField(verbose_name="Sanction")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name='punishments', verbose_name="Inscription de l'élève")
    incident_date = models.DateField(verbose_name="Date de l'incident")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Statut")
    
    class Meta:
        ordering = ['-incident_date', '-created_at']
        verbose_name = "Punition"
        verbose_name_plural = "Punitions"
        
    def __str__(self) -> str:
        return f"Punition pour {self.enrollment.student.first_name} {self.enrollment.student.last_name} - {self.incident_date}"