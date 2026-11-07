from django import forms

from apps.accounts.models import Gender
from apps.tools.styling import style_form_fields
from .models import SchoolClass, StudentGuardian


class EnrollmentForm(forms.Form):
    first_name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={
        "placeholder" : "Prenom",
    }))
    middle_name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={
        "placeholder" : "Postnom",
    }))
    last_name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={
        "placeholder" : "Nom",
    }))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    profile_img = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        "id": "upload-img",
    }))
    gender = forms.ChoiceField(choices=Gender.choices, widget=forms.Select(attrs={}))
    relation = forms.ChoiceField(choices=StudentGuardian.Relationship.choices, widget=forms.Select(attrs={}))
    school_class = forms.ModelChoiceField(queryset=SchoolClass.objects.all(), widget=forms.Select(attrs={}))

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        style_form_fields(self)
    
