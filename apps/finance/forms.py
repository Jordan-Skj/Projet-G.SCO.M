from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from django import forms
from django.db.models import TextChoices
from django.utils import timezone

from apps.tools.styling import style_form_fields
from apps.students.models import Enrollment
from .models import MONEY_STEP, Exemption, Fee
from .services import get_exchange_rate


class MobileMoneyOperator(TextChoices):
    VODACOM = 'vodacom_cd', "Mpesa"
    ORANGE = 'orange_cd', "Orange Money"
    AIRTEL = 'airtel_cd', "Airtel Money"


class ExemptionForm(forms.ModelForm):
    class Meta:
        model = Exemption
        fields = ['fee', 'expire_at', 'description']

    def __init__(self, *args, enrollment : Enrollment | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.enrollment = enrollment
        if self.enrollment:
            fees = Fee.objects.filter(
                school_class=self.enrollment.school_class,
                academic_year=self.enrollment.academic_year,
            )
            self.fields['fee'].queryset = Fee.objects.filter(
                pk__in=[fee.pk for fee in fees if fee.outstanding_for(self.enrollment) > 0]
            )
        style_form_fields(self)
            
    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        if cleaned_data.get('expire_at') and cleaned_data['expire_at'] <= timezone.now():
            self.add_error('expire_at', "La date d'expiration choisie est deja passe")
            
        return cleaned_data


class MobileMoneyPaymentForm(forms.Form):
    operator = forms.ChoiceField(choices=MobileMoneyOperator.choices)
    phone_number = forms.CharField(widget=forms.TelInput(attrs={
        'placeholder': "801234567"
    }))

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        style_form_fields(self)


class FeePaymentForm(forms.Form):
    fee = forms.ModelChoiceField(Fee.objects.none(), widget=forms.Select(attrs={
        'data-step': 'fee-info'
    }))
    amount = forms.DecimalField(
        min_value=Decimal('0.01'),
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'data-step': 'fee-info'
        }),
    )
    currency = forms.ChoiceField(choices=Fee.Currency.choices, widget=forms.Select(attrs={
        'data-step': 'fee-info'
    }))
    operator = forms.ChoiceField(choices=MobileMoneyOperator.choices, widget=forms.Select(attrs={
        'data-step': 'payment-method'
    }))
    phone_number = forms.CharField(widget=forms.TelInput(attrs={
        'data-step': 'payment-method'
    }))

    def __init__(self, *args, enrollment : Enrollment | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.enrollment = enrollment
        if self.enrollment:
            fees = Fee.objects.filter(
                school_class=self.enrollment.school_class,
                academic_year=self.enrollment.academic_year,
            )
            fees_with_balance = [
                fee.pk for fee in fees
                if fee.outstanding_for(self.enrollment) > 0
            ]
            self.fields['fee'].queryset = Fee.objects.filter(pk__in=fees_with_balance)

        style_form_fields(self)

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        if not cleaned_data:
            return None

        fee = cleaned_data.get('fee')
        amount = cleaned_data.get('amount')
        currency = cleaned_data.get('currency')
        if self.enrollment and fee and amount and currency:
            exchange_rate = get_exchange_rate(currency, fee.currency)
            if exchange_rate is None:
                self.add_error(
                    'currency',
                    "Le taux de conversion de cette devise n'est pas configuré.",
                )
            else:
                amount_in_fee_currency = (amount * exchange_rate).quantize(
                    MONEY_STEP, rounding=ROUND_HALF_UP
                )
                if amount_in_fee_currency > fee.outstanding_for(self.enrollment):
                    self.add_error(
                        'amount',
                        "Le montant dépasse le solde restant pour ces frais.",
                    )

        return cleaned_data