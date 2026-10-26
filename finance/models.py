from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from students.models import AcademicYear, Enrollment, SchoolClass

MONEY_STEP: Decimal = Decimal('0.01')


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
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.school_class} - {self.academic_year}"

    def outstanding_for(self, enrollment: Enrollment) -> Decimal:
        """Remaining amount (in the fee currency). Only verified payments count."""
        verified_payments: FeePaymentQuerySet = self.fee_payments.verified().filter(
            enrollment=enrollment
        )
        total_paid: Decimal = sum(
            (payment.amount_in_fee_currency() for payment in verified_payments),
            Decimal('0.00'),
        )
        return max(self.amount_due - total_paid, Decimal('0.00'))


class FeePaymentQuerySet(models.QuerySet["FeePayment"]):
    def verified(self) -> "FeePaymentQuerySet":
        return self.filter(status=FeePayment.Status.VERIFIED)


class FeePayment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Espèces'
        MOBILE_MONEY = 'mobile_money', 'Mobile Money'

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente de vérification'
        VERIFIED = 'verified', 'Vérifié'
        REJECTED = 'rejected', 'Rejeté'
        VOIDED = 'voided', 'Annulé'

    class ReceiptStatus(models.TextChoices):
        NOT_SUBMITTED = 'not_submitted', 'Reçu non remis'
        SUBMITTED = 'submitted', 'Reçu remis'

    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT, related_name='fee_payments', verbose_name='Inscription de l\'élève')
    fee = models.ForeignKey(Fee, on_delete=models.PROTECT, related_name='fee_payments', verbose_name='Frais concernés')
    amount_paid = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='Montant payé',
        validators=[MinValueValidator(MONEY_STEP)],
    )
    payment_date = models.DateField(verbose_name='Date de paiement')
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, verbose_name='Méthode de paiement')
    payment_currency = models.CharField(max_length=3, choices=Fee.Currency.choices, default=Fee.Currency.USD, verbose_name='Devise du paiement')
    exchange_rate = models.DecimalField(
        max_digits=20, decimal_places=10, default=Decimal('1'),
        validators=[MinValueValidator(Decimal('0.0000000001'))],
        verbose_name='Taux de change',
        help_text='Montant dans la devise des frais = montant payé × taux. Vaut 1 si les devises sont identiques.',
    )
    receipt_reference = models.CharField(max_length=100, unique=True, verbose_name='Numéro du reçu')
    receipt_status = models.CharField(max_length=20, choices=ReceiptStatus.choices, default=ReceiptStatus.NOT_SUBMITTED, verbose_name='Statut du reçu')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name='Statut du paiement')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='submitted_fee_payments', verbose_name='Soumis par')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name='verified_fee_payments', verbose_name='Vérifié par')
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name='Vérifié le')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')

    objects = FeePaymentQuerySet.as_manager()

    class Meta:
        ordering = ['-payment_date', '-created_at']
        verbose_name = 'Paiement des frais'
        verbose_name_plural = 'Paiements des frais'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_paid__gt=0), name='fee_payment_amount_must_be_positive'
            ),
            models.CheckConstraint(
                condition=models.Q(exchange_rate__gt=0), name='fee_payment_exchange_rate_must_be_positive'
            ),
            models.CheckConstraint(
                condition=~models.Q(status='verified') | models.Q(verified_by__isnull=False, verified_at__isnull=False),
                name='fee_payment_verified_needs_verifier',
            ),
        ]

    def clean(self) -> None:
        super().clean()
        errors: dict[str, str] = {}

        if self.enrollment_id and self.fee_id:
            if (
                self.enrollment.school_class_id != self.fee.school_class_id
                or self.enrollment.academic_year_id != self.fee.academic_year_id
            ):
                errors['fee'] = (
                    "Ces frais ne correspondent pas à la classe "
                    "et à l'année scolaire de l'inscription."
                )

            if self.exchange_rate is not None:
                same_currency: bool = self.payment_currency == self.fee.currency
                if same_currency and self.exchange_rate != Decimal('1'):
                    errors['exchange_rate'] = (
                        'Le taux de change doit être 1 si la devise du paiement '
                        'est la même que celle des frais.'
                    )
                elif not same_currency and self.exchange_rate == Decimal('1'):
                    errors['exchange_rate'] = (
                        'Le taux de change ne peut pas être 1 si les devises sont différentes.'
                    )

        if errors:
            raise ValidationError(errors)

    def save(self, *args: object, **kwargs: object) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def amount_in_fee_currency(self) -> Decimal:
        return (self.amount_paid * self.exchange_rate).quantize(MONEY_STEP, rounding=ROUND_HALF_UP)

    def __str__(self) -> str:
        return f'{self.enrollment.student} - {self.fee.name} - {self.amount_paid} {self.payment_currency} - Numero du reçu: {self.receipt_reference}'