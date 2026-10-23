from django.contrib import admin
from unfold.admin import UnfoldAdmin
from accounts.models import Parent

# Register your models here.
@admin.register(Parent)
class ParentAdmin(UnfoldAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    ordering = ('last_name', 'middle_name', 'first_name')