from django import forms

from apps.studies.models import Test
from apps.students.models import Enrollment
from apps.tools.styling import style_form_fields
from .models import Justification

class JustificationForm(forms.ModelForm):
    class Meta:
        model = Justification
        fields = ['description', 'type', 'other_type', 'reason', 'missed_test', 'absence_record', 'lateness_record']

    def __init__(self, *args, enrollment: Enrollment | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if enrollment:
            self.fields['absence_record'].queryset = enrollment.absences.filter(status='not_justified').order_by('-date')
            self.fields['lateness_record'].queryset = enrollment.latenesses.filter(status='not_justified').order_by('-created_at')
            self.fields['missed_test'].queryset = Test.objects.filter(course__school_class=enrollment.school_class).order_by('date')
        else:
            self.fields['absence_record'].queryset = self.fields['absence_record'].queryset.none()
            self.fields['lateness_record'].queryset = self.fields['lateness_record'].queryset.none()
            self.fields['missed_test'].queryset = self.fields['missed_test'].queryset.none()
        style_form_fields(self)
