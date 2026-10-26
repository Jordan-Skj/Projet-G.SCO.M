from django.conf import settings
from django.db import models

from students.models import Enrollment


class Punishment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Sanction à exécuter'
        IN_PROGRESS = 'in_progress', 'Sanction en cours'
        COMPLETED = 'completed', 'Sanction exécutée'
        CANCELED = 'canceled', 'Sanction annulée'

    class ReturnToClass(models.TextChoices):
        NOT_RESTRICTED = 'not_restricted', 'Aucune restriction'
        NOT_AUTHORIZED = 'not_authorized', 'Retour en classe non autorisé'
        AUTHORIZED = 'authorized', 'Retour en classe autorisé'

    violated_article = models.CharField(max_length=255, verbose_name="Article du reglement scolaire violé")
    description = models.TextField(verbose_name="Description de la punition")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    punished_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='issued_punishments', verbose_name="Sanctionné par")
    sanction = models.TextField(verbose_name="Sanction")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name='punishments', verbose_name="Inscription de l'élève")
    incident_date = models.DateField(verbose_name="Date de l'incident")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Statut")

    # No default on purpose: the person recording the punishment must decide.
    return_to_class = models.CharField(
        max_length=20,
        choices=ReturnToClass.choices,
        verbose_name="Retour en classe",
    )
    authorized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='authorized_returns',
        verbose_name="Retour autorisé par",
    )
    authorized_at = models.DateTimeField(null=True, blank=True, verbose_name="Retour autorisé le")

    class Meta:
        ordering = ['-incident_date', '-created_at']
        verbose_name = "Punition"
        verbose_name_plural = "Punitions"
        constraints = [
            models.CheckConstraint(
                condition=(
                    ~models.Q(return_to_class='authorized')
                    | models.Q(authorized_by__isnull=False, authorized_at__isnull=False)
                ),
                name='punishment_authorized_return_needs_authorizer',
            ),
        ]

    def blocks_class_access(self) -> bool:
        """True while the student must not return to class because of this punishment."""
        return (
            self.status != self.Status.CANCELED
            and self.return_to_class == self.ReturnToClass.NOT_AUTHORIZED
        )

    def __str__(self) -> str:
        student = self.enrollment.student
        return f"Punition pour {student.first_name} {student.last_name} - {self.incident_date}"