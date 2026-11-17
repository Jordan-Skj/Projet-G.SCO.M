from django.conf import settings
from django.db import models

from apps.studies.models import Test
from apps.students.models import Enrollment

class Absence(models.Model):
    class Status(models.TextChoices):
        JUSTIFIED = 'justified', "Justifiee"
        NOT_JUSTIFIED = 'not_justified', "Non justifiee"
        ISSUE_BY_SCHOOL = 'issue_by_school', "Retourne par l'school"
        PANILIZED = 'penalized', "Deja sanctionnee"
        
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, verbose_name="Eleve concerne", related_name='absences')
    date = models.DateField(auto_now_add=True, verbose_name="Date de l'absence")
    status = models.CharField(max_length=30, choices=Status.choices, verbose_name="Statut")
    
    class Meta:
        ordering = ['-date']
        
    def __str__(self) -> str:
        return f"Absence de l'eleve {self.enrollment.student} au {self.date}"
    
class Lateness(models.Model):
    class Status(models.TextChoices):
        JUSTIFIED = 'justified', "Justifiee"
        NOT_JUSTIFIED = 'not_justified', "Non justifiee"
        PANILIZED = 'penalized', "Deja sanctionnee"
        
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, verbose_name="Eleve concerne", related_name='latenesses')
    arrived_at = models.DateTimeField(auto_now_add=True, verbose_name="Date et heure de l'arrivee")
    status = models.CharField(max_length=30, choices=Status.choices, verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Retard de l'eleve {self.enrollment.student} au {self.arrived_at}"

class Justification(models.Model):
    class Status(models.TextChoices):
        APPROVED = 'approved', "Approuve"
        REJECTED = 'rejected', "Rejecte"
        PENDING = 'pending', "En cours de verification"
        EXPIRED = 'expired', "N'est plus prise en compte"
        
    class Type(models.TextChoices):
        ABSENCE = 'absence', "Absence"
        LATENESS = 'lateness', "Retard"
        EARLY_DEPARTURE = 'early_departure', "Detard avant la fin des cours"
        MISSED_EXAM = 'missed_exam', "Examen manque"
        MISSED_ASSIGNMENT = 'missed_assignment', "Devoir non fait"
        MISSED_LIBRARY_STUDIES = 'missed_library_studies', "Absence aux etudes de la bibliotheque"
        UNIFORM_VIOLATION = 'uniform_violation', "Violation de la tenue exigee"
        EXEMPTION = 'exemption', "Demande d'autorisation de non respect du reglement scolaire"
        OTHER = 'other', "Autre"
        
    description = models.TextField(verbose_name="Description")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, verbose_name="Pour l'eleve", related_name='justifications')
    status = models.CharField(max_length=40, choices=Status.choices)
    type = models.CharField(max_length=60, choices=Type.choices, verbose_name="Justification pour :")
    other_type = models.CharField(max_length=120, null=True, blank=True)
    reason = models.CharField(verbose_name="La raison")
    missed_test = models.ForeignKey(Test, on_delete=models.PROTECT, verbose_name="Epreuve manque", null=True, blank=True)
    absence_record = models.ForeignKey(Absence, on_delete=models.PROTECT, verbose_name="Absence concerne", null=True, blank=True)
    lateness_record = models.ForeignKey(Lateness, on_delete=models.PROTECT, verbose_name="Retard concerne", null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateField(verbose_name="Date d'exipiration")
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(status='approved') | models.Q(approved_by__isnull=False, approved_at__isnull=False),
                name='justification_approved_needs_approved_by'
            ),
            models.CheckConstraint(
                condition=~models.Q(type='other') | models.Q(other_type__isnull=False),
                name='justification_other_needs_other_type'
            ),
            models.CheckConstraint(
                condition=~models.Q(type='missed_exam') | models.Q(missed_test__isnull=False),
                name='justification_missed_test_needs_type'
            ),
            models.CheckConstraint(
                condition=~models.Q(type='absence') | models.Q(absence_record__isnull=False),
                name='justification_absence_needs_absence_record'
            ),
            models.CheckConstraint(
                condition=~models.Q(type='lateness') | models.Q(lateness_record__isnull=False),
                name='justification_lateness_needs_lateness_record'
            ),
        ]
        
    def __str__(self) -> str:
        return f"Justification pour {self.status.lower()} de l'eleve {self.enrollment.student}"
        


class Punishment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', "Sanction à exécuter"
        IN_PROGRESS = 'in_progress', "Sanction en cours"
        COMPLETED = 'completed', "Sanction exécutée"
        CANCELED = 'canceled', "Sanction annulée"

    class ReturnToClass(models.TextChoices):
        NOT_RESTRICTED = 'not_restricted', "Aucune restriction"
        NOT_AUTHORIZED = 'not_authorized', "Retour en classe non autorisé"
        AUTHORIZED = 'authorized', "Retour en classe autorisé"

    violated_article = models.CharField(max_length=255, verbose_name="Article du reglement scolaire violé")
    description = models.TextField(verbose_name="Description de la punition")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    punished_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='issued_punishments', verbose_name="Sanctionné par")
    sanction = models.TextField(verbose_name="Sanction")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name='punishments', verbose_name="Inscription de l'élève")
    incident_date = models.DateField(verbose_name="Date de l'incident")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Statut")

    # No default on purpose: the person recording the punishment must decide.
    return_to_class = models.CharField(max_length=20, choices=ReturnToClass.choices, verbose_name="Retour en classe")
    authorized_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True, related_name='authorized_returns',verbose_name="Retour autorisé par")
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
        permissions = [
            ('authorize_return_to_class', 'Peut autoriser le retour en classe'),
            ('check_class_access', "Peut vérifier les restrictions d'accès en classe"),
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
