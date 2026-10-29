from django import forms
from .localisation import KINSHASA

# Updated to be a single string and work in both light and dark modes
INPUT_CLASSES = (
    "block w-full rounded-lg border px-4 py-3 text-sm "
    "bg-white text-gray-900 border-gray-300 placeholder:text-gray-400 "
    "dark:bg-[#191B20] dark:text-gray-100 dark:border-gray-700 dark:placeholder:text-gray-500 "
    "shadow-sm transition-all duration-200 "
    "hover:border-gray-400 dark:hover:border-gray-500 "
    "focus:border-[#D95745] dark:focus:border-[#D95745] "
    "focus:outline-none focus:ring-4 focus:ring-[#D95745]/20 "
    "disabled:cursor-not-allowed disabled:opacity-50"
)

class ParentLoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "placeholder": "Email",
        "class": INPUT_CLASSES,
    }))
    password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={
        "placeholder": "Mot de passe",
        "class": INPUT_CLASSES,
    }))

class ParentSignUpForm(forms.Form):
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        "placeholder" : "Nom",
        "class": f"identity {INPUT_CLASSES}",
    }))
    middle_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        "placeholder": "Postnom",
        "class": f"identity {INPUT_CLASSES}",
    }))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        "placeholder": "Prenom",
        "class": f"identity {INPUT_CLASSES}",
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "placeholder": "Email",
        "class": f"electronic_coordonates {INPUT_CLASSES}",
    }))
    phone_number = forms.IntegerField(required=True, widget=forms.TextInput(attrs={
        "placeholder": "Numero de telephone",
        "type": "tel",
        "class": f"electronic_coordonates {INPUT_CLASSES}",
    }))
    alternate_phone_number = forms.IntegerField(required=False, widget=forms.TextInput(attrs={
        "placeholder": "Numero de telephone alternative",
        "type": "tel",
        "class": f"electronic_coordonates {INPUT_CLASSES}",
    }))
    township = forms.ChoiceField(
        choices=[("", "Choisir une commune")] + [(name, name) for name in KINSHASA],
        widget=forms.Select(attrs={
            "class": f"adress {INPUT_CLASSES}",
            "id": "id_commune",
        }),
    )
    quater = forms.ChoiceField(
        choices=[("", "Choisir d'abord une commune")],
        widget=forms.Select(attrs={
            "class": f"adress {INPUT_CLASSES}",
            "id": "id_quartier",
            "disabled": True,
        }),
    )
    street = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        "placeholder": "Avenue / rue",
        "class": f"adress {INPUT_CLASSES}",
    }))
    street_number = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={
        "placeholder": "Numéro (ex: 12)",
        "class": f"adress {INPUT_CLASSES}",
    }))
    password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={
        "placeholder": "Mot de passe",
        "class": f"security {INPUT_CLASSES}",
    }))
    confirm_password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={
        "placeholder": "Confirmer votre mot de passe",
        "class": f"security {INPUT_CLASSES}",
    }))
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        township = self.data.get("township", "") if self.is_bound else ""
        if township in KINSHASA:
            quaters = KINSHASA[township]
            self.fields["quater"].choices = [("", "Choisir un quartier")] + [(quater, quater) for quater in quaters]
            
    def clean(self) -> dict[str, object]:
        cleaned_data = super().clean()
        township = cleaned_data.get("township")
        quater = cleaned_data.get("quater")
        if township and quater:
            if quater not in KINSHASA.get(township, []):
                self.add_error("quater", "Ce quartier ne correspond pas à la commune choisie.")

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password") 
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Les mots de passe ne correspondent pas.")
        return cleaned_data