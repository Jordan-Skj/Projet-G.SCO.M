from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(label='Nom complet', max_length=150)
    email = forms.EmailField(label='Adresse e-mail')
    objet = forms.ChoiceField(label='Objet', required=False, choices=[
        ('', 'Sélectionnez un objet…'), ('inscription', 'Inscription'),
        ('infos', 'Informations générales'), ('partenariat', 'Partenariat'), ('autre', 'Autre'),
    ])
    message = forms.CharField(label='Votre message', max_length=10000)
