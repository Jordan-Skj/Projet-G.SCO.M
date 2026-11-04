from datetime import date
from typing import Any

from django import forms
from django.db.models import TextChoices

from tools.styling import style_form_fields
from students.models import Enrollment
from .models import Exemption, Fee, FeePayment


class MobileMoneyOperator(TextChoices):
    AFRICELL = 'africell', "Afrimoney"
    VODACOM = 'vodacom', "Mpesa"
    ORANGE = 'orange', "Orange Money"
    AIRTEL = 'airtel', "Airtel Money"

class ExemptionForm(forms.ModelForm):
    class Meta:
        model = Exemption
        fields = ['fee', 'expire_at', 'description']

    def __init__(self, *args, enrollment : Enrollment, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.enrollment = enrollment
        fees = Fee.objects.filter(school_class=self.enrollment.school_class)
        self.fields['fee'].queryset = Fee.objects.filter(
            pk__in=[fee.pk for fee in fees if fee.outstanding_for(self.enrollment) > 0]
        )
        style_form_fields(self)
            
    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        if cleaned_data.get('expire_at', date.today())  <= date.today():
            self.add_error('expire_at', "La date d'expiration choisie est deja passe")
            
        return cleaned_data

        
class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ['fee', 'amount_paid']
        
    def __init__(self, *args, enrollment : Enrollment, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.enrollment = enrollment
        self.fields.get('fee').queryset = Fee.objects.filter(school_class=self.enrollment.school_class)
        style_form_fields(self)
        
    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        if not cleaned_data:
            return None

        if isinstance(
            cleaned_data.get('fee', None),
            Fee
        ):
            return cleaned_data

        if cleaned_data.get('amount_paid') > self.fields.get('fee').outstanding_for(self.enrollment):
            self.add_error('amount_paid', "Le montant a paye doit etre inferieur ")


        return cleaned_data

class MobileMoneyPaymentForm(forms.Form):
    operator = forms.ChoiceField(choices=MobileMoneyOperator.choices, widget=forms.Select(attrs={}))
    phone_number = forms.CharField(widget=forms.TelInput(attrs={
        'placeholder': "801234567"
    }))

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        style_form_fields(self)

