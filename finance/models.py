from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from students.models import AcademicYear, Enrollment, SchoolClass

class Fee(models.Model):
    class Currency(models.TextChoices):
        USD = 'USD', 'Dollar américain'
        CDF = 'CDF', 'Franc congolais'

    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name='fees', verbose_name='Classe')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name='fees', verbose_name='Année scolaire')
    name = models.CharField(max_length=100, verbose_name='Nom des frais', help_text='Ex : Minerval, inscription, frais d\'examen')
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Montant à payer')
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD, verbose_name='Devise')
    due_date = models.DateField(null=True, blank=True, verbose_name='Date limite de paiement')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_fees', verbose_name='Créé par')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    
    class Meta:
        ordering = ['academic_year', 'school_class', 'name']
        verbose_name = 'Frais scolaire'
        verbose_name_plural = 'Frais scolaires'
        constraints = [
            models.UniqueConstraint(
                fields=['school_class', 'academic_year', 'name'], name='unique_fee_class_year_name'
            ),
            models.CheckConstraint(
                condition=models.Q(amount_due__gt=0), name='fee_amount_must_be_positive'
            )
        ]
        
    def __str__(self) -> str:
        return f"{self.name} - {self.school_class} - {self.academic_year}"
    
class FeePayment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Espèces'
        MOBILE_MONEY = 'mobile_money', 'Mobile Money'
        
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name='fee_payments', verbose_name='Inscription de l\'élève')
    fee = models.ForeignKey(Fee, on_delete=models.PROTECT, related_name='fee_payments', verbose_name='Frais concernés')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Montant payé')
    payment_date = models.DateField(verbose_name='Date de paiement')
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, verbose_name='Méthode de paiement')
    payment_currency = models.CharField(max_length=3, choices=Fee.Currency.choices, default=Fee.Currency.USD, verbose_name='Devise du paiement')
    receipt_reference = models.CharField(max_length=100, unique=True, verbose_name='Numéro du reçu')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='submitted_fee_payments', verbose_name='Soumis par')
    created_at = models.DateTimeField(auto_now_add=True)
    exchange_rate = models.DecimalField(max_digits=34, decimal_places=6, null=True, blank=True, verbose_name='Taux de change')
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
        verbose_name = 'Paiement des frais'
        verbose_name_plural = 'Paiements des frais'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_paid__gt=0), name='fee_payment_amount_must_be_positive'
            )
        ]
        
    def clean(self) -> None:
        super().clean()
        if not self.enrollment_id or not self.fee_id:
            return
        
        if self.enrollment.school_class_id != self.fee.school_class_id or self.enrollment.academic_year_id != self.fee.academic_year_id:
            raise ValidationError({'fee': (
                'Ces frais ne correspondent pas à la classe de l\'élève.'
                'et aussi à l\'année scolaire de l\'élève.'
            )})
            
    def __str__(self) -> str:
        return f'{self.enrollment.student} - {self.fee.name} - {self.amount_paid} {self.currency} - Numero du reçu: {self.receipt_reference}'