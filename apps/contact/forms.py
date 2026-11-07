from django import forms
from apps.tools.styling import style_form_fields

class ContactForm(forms.Form):
    name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': "Nom"
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': "Email"
    }))
    objet = forms.ChoiceField(label="Objet", required=False,
        choices=[
            ("", "Sélectionnez un objet…"), ('enrollment', "Inscription"),
            ('infos', "Informations générales"), ('partnership', "Partenariat"), ("other", "Autre"),
        ],
        widget=forms.Select(attrs={})
    )
    message = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': "Votre message"
    }))

    def __int__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        style_form_fields(self)
