from django.core.validators import FileExtensionValidator
from django import forms

from apps.accounts.models import Gender
from apps.tools.styling import style_form_fields
from .models import (
    ENROLLMENT_REQUIRED_DOCUMENT_TYPES,
    EnrollmentDocument,
    SchoolClass,
    StudentGuardian,
)


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
    birth_certificate = forms.FileField(
        label="Acte de naissance (PDF, JPG ou PNG)",
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'}),
    )
    student_photo = forms.ImageField(
        label="Photo récente de l'enfant",
        widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}),
    )
    gender = forms.ChoiceField(choices=Gender.choices, widget=forms.Select(attrs={}))
    relation = forms.ChoiceField(choices=StudentGuardian.Relationship.choices, widget=forms.Select(attrs={}))
    school_class = forms.ModelChoiceField(queryset=SchoolClass.objects.all(), widget=forms.Select(attrs={}))

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        style_form_fields(self)

    def clean(self):
        cleaned_data = super().clean()
        self._validate_file_sizes(cleaned_data)
        return cleaned_data

    def _validate_file_sizes(self, cleaned_data) -> None:
        max_size = 10 * 1024 * 1024
        for field_name in ('birth_certificate', 'student_photo'):
            uploaded_file = cleaned_data.get(field_name)
            if uploaded_file and uploaded_file.size > max_size:
                self.add_error(field_name, "Le fichier ne doit pas dépasser 10 Mo.")


class EnrollmentDocumentResubmissionForm(forms.Form):
    def __init__(self, *args, enrollment, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.enrollment = enrollment
        documents_by_type = {
            document.document_type: document
            for document in enrollment.documents.all()
        }
        self.documents_to_submit = []
        for document_type in ENROLLMENT_REQUIRED_DOCUMENT_TYPES:
            document = documents_by_type.get(document_type)
            if document and document.status != EnrollmentDocument.Status.REJECTED:
                continue
            self.documents_to_submit.append((document_type, document))
            label = (
                document.get_document_type_display()
                if document
                else dict(EnrollmentDocument.Type.choices)[document_type]
            )
            if document_type == EnrollmentDocument.Type.STUDENT_PHOTO:
                self.fields[document_type] = forms.ImageField(
                    label=label,
                    widget=forms.ClearableFileInput(attrs={'accept': 'image/*'}),
                )
            else:
                self.fields[document_type] = forms.FileField(
                    label=f"{label} (PDF, JPG ou PNG)",
                    validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
                    widget=forms.ClearableFileInput(attrs={
                        'accept': '.pdf,.jpg,.jpeg,.png'
                    }),
                )
        style_form_fields(self)

    def clean(self):
        cleaned_data = super().clean()
        max_size = 10 * 1024 * 1024
        for field_name, uploaded_file in cleaned_data.items():
            if uploaded_file and uploaded_file.size > max_size:
                self.add_error(field_name, "Le fichier ne doit pas dépasser 10 Mo.")
        return cleaned_data
    
