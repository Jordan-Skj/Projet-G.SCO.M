from django import forms
from django.conf import settings

def style_form_fields(form: forms.Form | forms.ModelForm) -> None:
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs.update({
                'class': settings.CHECKBOX_CLASSES
            })
        elif isinstance(field.widget, forms.Select):
            field.widget.attrs.update({
                'class': settings.SELECT_CLASSES
            })
        elif isinstance(field.widget, forms.Textarea):
            field.widget.attrs.update({
                'class': settings.TEXTAREA_CLASSES
            })
        elif isinstance(field.widget, forms.FileInput):
            field.widget.attrs.update({
                'class': settings.FILE_INPUT_CLASSES
            })
        elif isinstance(field.widget, forms.RadioSelect):
            field.widget.attrs.update({
                'class': settings.RADIO_CLASSES
            })
        elif isinstance(field.widget, forms.DateInput) or isinstance(field.widget, forms.DateTimeInput):
            field.widget.attrs.update({
                'class': settings.DATE_INPUT_CLASSES
            })
        else:
            field.widget.attrs.update({
                "class": settings.TEXT_INPUT_CLASSES
            })