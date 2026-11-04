from django import forms

from studies.models import Test
from students.models import Enrollment
from tools.styling import style_form_fields
from .models import Absence, Justification, Lateness

class JustificationForm(forms.ModelForm):
    class Meta:
        model = Justification
        fields = ['description', 'status', 'type', 'other_type', 'reason', 'missed_test', 'absence_record', 'lateness_record']

    def __init__(self, *args, enrollment: Enrollment, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['absence_record'].queryset = Absence.objects.filter(enrollment=enrollment, status='not_justified').order_by('-date')
        self.fields['lateness_record'].queryset = Lateness.objects.filter(enrollment=enrollment, status='not_justified').order_by('-created_at')
        self.fields['missed_test'].queryset = Test.objects.filter(course__school_class=enrollment.school_class).order_by('date')
        style_form_fields(self)

