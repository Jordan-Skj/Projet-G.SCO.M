from django import forms

FILE_INPUT_CLASSES = (
    "block w-full rounded-lg border border-gray-300 text-sm "
    "bg-white text-gray-700 "
    "dark:bg-[#191B20] dark:text-gray-300 dark:border-gray-700 "
    "file:mr-4 file:cursor-pointer file:rounded-md file:border-0 "
    "file:bg-[#D95745]/10 file:px-4 file:py-2.5 "
    "file:text-sm file:font-semibold file:text-[#D95745] "
    "hover:file:bg-[#D95745]/20 "
    "dark:file:bg-[#D95745]/15 "
    "dark:file:text-[#F08070] "
    "transition-all duration-200 "
    "focus:outline-none focus:ring-4 focus:ring-[#D95745]/20 "
    "disabled:cursor-not-allowed disabled:opacity-50"
)

SELECT_CLASSES = (
    "block w-full appearance-none rounded-lg border px-4 py-3 pr-10 text-sm "
    "bg-white text-gray-900 border-gray-300 "
    "dark:bg-[#191B20] dark:text-gray-100 dark:border-gray-700 "
    "shadow-sm transition-all duration-200 cursor-pointer "
    "focus:border-[#D95745] focus:outline-none focus:ring-4 focus:ring-[#D95745]/20 "
    "disabled:cursor-not-allowed disabled:opacity-50"
)

TEXTAREA_CLASSES = (
    "block w-full min-h-32 rounded-lg border px-4 py-3 text-sm "
    "bg-white text-gray-900 border-gray-300 placeholder:text-gray-400 "
    "dark:bg-[#191B20] dark:text-gray-100 dark:border-gray-700 dark:placeholder:text-gray-500 "
    "shadow-sm transition-all duration-200 resize-y "
    "focus:border-[#D95745] focus:outline-none focus:ring-4 focus:ring-[#D95745]/20 "
    "disabled:cursor-not-allowed disabled:opacity-50"
)

TEXT_INPUT_CLASSES = (
    "block w-full rounded-lg border px-4 py-3 text-sm "
    "bg-white text-gray-900 border-gray-300 placeholder:text-gray-400 "
    "dark:bg-[#191B20] dark:text-gray-100 dark:border-gray-700 dark:placeholder:text-gray-500 "
    "shadow-sm transition-all duration-200 "
    "hover:border-gray-400 dark:hover:border-gray-500 "
    "focus:border-[#D95745] focus:outline-none focus:ring-4 focus:ring-[#D95745]/20 "
    "disabled:cursor-not-allowed disabled:opacity-50"
)

CHECKBOX_CLASSES = (
    "h-4 w-4 rounded border-gray-300 "
    "text-[#D95745] accent-[#D95745] "
    "focus:ring-2 focus:ring-[#D95745]/30 "
    "dark:border-gray-600 dark:bg-[#191B20] "
    "dark:checked:bg-[#D95745] "
    "disabled:cursor-not-allowed disabled:opacity-50"
)

RADIO_CLASSES = (
    "h-4 w-4 border-gray-300 text-[#D95745] "
    "accent-[#D95745] focus:ring-2 focus:ring-[#D95745]/30 "
    "dark:border-gray-600 dark:bg-[#191B20] "
    "disabled:cursor-not-allowed disabled:opacity-50"
)

DATE_INPUT_CLASSES = (
    "block w-full rounded-lg border px-4 py-3 text-sm "
    "bg-white text-gray-900 border-gray-300 "
    "dark:bg-[#191B20] dark:text-gray-100 dark:border-gray-700 "
    "shadow-sm transition-all duration-200 "
    "focus:border-[#D95745] focus:outline-none focus:ring-4 focus:ring-[#D95745]/20 "
    "disabled:cursor-not-allowed disabled:opacity-50 "
    "[color-scheme:light] dark:[color-scheme:dark]"
)


def style_form_fields(form: forms.Form | forms.ModelForm) -> None:
    for field in form.fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            field.widget.attrs.update({
                'class': CHECKBOX_CLASSES
            })
        elif isinstance(field.widget, forms.Select):
            field.widget.attrs.update({
                'class': SELECT_CLASSES
            })
        elif isinstance(field.widget, forms.Textarea):
            field.widget.attrs.update({
                'class': TEXTAREA_CLASSES
            })
        elif isinstance(field.widget, forms.FileInput):
            field.widget.attrs.update({
                'class': FILE_INPUT_CLASSES
            })
        elif isinstance(field.widget, forms.RadioSelect):
            field.widget.attrs.update({
                'class': RADIO_CLASSES
            })
        elif isinstance(field.widget, forms.DateInput) or isinstance(field.widget, forms.DateTimeInput):
            field.widget.attrs.update({
                'class': DATE_INPUT_CLASSES
            })
        else:
            field.widget.attrs.update({
                "class": TEXT_INPUT_CLASSES
            })