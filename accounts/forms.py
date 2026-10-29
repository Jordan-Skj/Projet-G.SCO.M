from django import forms
from .localisation import KINSHASA_QUARTIERS


INPUT_CLASSES = (
            "block w-full rounded-lg border border-gray-700 "
            "bg-[#191B20] px-4 py-3 text-sm text-gray-100 "
            "placeholder:text-gray-500 "
            "shadow-sm transition-all duration-200 "
            "hover:border-gray-600 "
            "focus:border-[#D95745] focus:outline-none "
            "focus:ring-4 focus:ring-[#D95745]/15 "
            "disabled:cursor-not-allowed "
            "disabled:opacity-50"
        ),

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
        "class": ("identity",) + INPUT_CLASSES,
    }))
    middle_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        "placeholder": "Postnom",
        "class": ("identity",) + INPUT_CLASSES,
    }))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        "placeholder": "Prenom",
        "class": ("identity",) + INPUT_CLASSES,
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "placeholder": "Email",
        "class": ("electronic_coordonates",) + INPUT_CLASSES,
    }))
    phone_number = forms.IntegerField(required=True, widget=forms.TextInput(attrs={
        "placeholder": "Numero de telephone",
        "type": "tel",
        "class": ("electronic_coordonates",) + INPUT_CLASSES,
    }))
    alternate_phone_number = forms.IntegerField(widget=forms.TextInput(attrs={
        "placeholder": "Numero de telephone alternative",
        "type": "tel",
        "class": ("electronic_coordonates",) + INPUT_CLASSES,
    }))
    township = forms.ChoiceField(
        choices=[("", "Choisir une commune")]
        + [(name, name) for name in KINSHASA_QUARTIERS],
        widget=forms.Select(attrs={
            "class": ("adress", ) + INPUT_CLASSES,
            "id": "id_commune",
        }),
    )
    quater = forms.ChoiceField(
        choices=[("", "Choisir d'abord une commune")],
        widget=forms.Select(attrs={
            "class": ("adress", ) + INPUT_CLASSES,
            "id": "id_quartier",
            "disabled": True,
        }),
    )
    street = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        "placeholder": "Avenue / rue",
        "class": ("adress",) + INPUT_CLASSES,
    }))
    password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={
        "placeholder": "Mot de passe",
        "class": ("security",) + INPUT_CLASSES,
    }))
    confirm_password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={
        "placeholder": "Confirmer votre mot de passe",
        "class": ("security",) + INPUT_CLASSES,
    }))
    
    
    def __init__(self, *args : object, **kwargs : object) -> None:
        super().__init__(*args, **kwargs)

        township = self.data.get("township", "") if self.is_bound else ""
        if township in KINSHASA_QUARTIERS:
            quaters = KINSHASA_QUARTIERS[township]
            
            self.fields["quater"].choices = [
                ("", "Choisir un quartier"),
                ((quater, quater) for quater in quaters)
            ]
            
    def clean(self) -> dict[str, object]:
        cleaned_data = super().clean()
        
        # Check for quater is correctly chosen
        township = cleaned_data.get("township")
        quater = cleaned_data.get("quater")
        if township and quater:
            if quater not in KINSHASA_QUARTIERS.get(township, []):
                self.add_error(
                    "quater",
                    "Ce quartier ne correspond pas à la commune choisie.",
                )

        # Check if passwords matches
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password") 
        if password and confirm_password and password != confirm_password:
            self.add_error(
                "confirm_password",
                "Les mot de passes ne correspondent pas."
            )
        return cleaned_data
                  