from django.db import models
from students.models import Enrollment

class Punishment(models.Model):
    violated_article = models.CharField(max_length=255, verbose_name="Article du reglement scolaire violé")
    description = models.TextField(verbose_name="Description de la punition")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    sanction = models.TextField(verbose_name="Sanction")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name='punishments', verbose_name="Inscription de l'élève")
    incident_date = models.DateField(verbose_name="Date de l'incident")
    
    class Meta:
        ordering = ['-incident_date', '-created_at']
        verbose_name = "Punition"
        verbose_name_plural = "Punitions"
        
    def __str__(self) -> str:
        return f"Punition pour {self.enrollment.student.first_name} {self.enrollment.student.last_name} - {self.incident_date}"