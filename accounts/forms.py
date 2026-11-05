from typing import Any

from django import forms

from tools.styling import SELECT_CLASSES, TEXT_INPUT_CLASSES, style_form_fields
from accounts.models import Gender
from .localisation import KINSHASA



class ParentLoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': "Email",
    }))
    password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={
        'placeholder': "Mot de passe",
    }))
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        style_form_fields(self)
        

class ParentSignUpForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'placeholder' : "Nom",
        'class': f'identity {TEXT_INPUT_CLASSES}',
    }))
    middle_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'placeholder': "Postnom",
        'class': f'identity {TEXT_INPUT_CLASSES}',
    }))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'placeholder': "Prenom",
        'class': f'identity {TEXT_INPUT_CLASSES}',
    }))
    gender = forms.ChoiceField(choices=Gender.choices, widget=forms.Select(attrs={
            'class': f'identity {SELECT_CLASSES}',
        }),
    )
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': "Email",
        'class': f'electronic_coordonates {TEXT_INPUT_CLASSES}',
    }))
    phone_number = forms.IntegerField(required=True, widget=forms.TextInput(attrs={
        'placeholder': "Numero de telephone",
        'type': 'tel',
        'class': f'electronic_coordonates {TEXT_INPUT_CLASSES}',
    }))
    alternate_phone_number = forms.IntegerField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Numero de telephone alternative",
        'type': 'tel',
        'class': f'electronic_coordonates {TEXT_INPUT_CLASSES}',
    }))
    township = forms.ChoiceField(
        choices=[("", "Choisir une commune")] + [(name, name) for name in KINSHASA],
        widget=forms.Select(attrs={
            'class': f'adress {SELECT_CLASSES}',
            'id': 'id_commune',
        }),
    )
    quarter = forms.ChoiceField(
        choices=[("", "Choisir d'abord une commune")],
        widget=forms.Select(attrs={
            'class': f'adress {SELECT_CLASSES}',
            'id': 'id_quartier',
            'disabled': True,
        }),
    )
    street = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'placeholder': "Avenue / rue",
        'class': f'adress {TEXT_INPUT_CLASSES}',
    }))
    street_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={
        'placeholder': "Numéro (ex: 12)",
        'class': f'adress {TEXT_INPUT_CLASSES}',
    }))
    password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={
        'placeholder': "Mot de passe",
        'class': f'security {TEXT_INPUT_CLASSES}',
    }))
    confirm_password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={
        'placeholder': "Confirmer votre mot de passe",
        'class': f'security {TEXT_INPUT_CLASSES}',
    }))
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        township = self.data.get('township') if self.is_bound else ''
        if township in KINSHASA:
            quarters = KINSHASA[township]
            self.fields.get('quarter').choices = [("", "Choisir un quartier")] + [(quarter, quarter) for quarter in quarters]
            
    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()
        
        if not cleaned_data:
            return super().clean()
        
        township = cleaned_data.get('township')
        quarter = cleaned_data.get('quarter')
        if township and quarter:
            if quarter not in KINSHASA.get(township, []):
                self.add_error('quarter', "Ce quartier ne correspond pas à la commune choisie.")

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password') 
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Les mots de passe ne correspondent pas.")
        return cleaned_data