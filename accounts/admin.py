from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display : tuple[str, ...] = ('username', 'email', 'first_name', 'last_name', 'role')
    list_filter : tuple[str, ...] = ('role',)
    search_fields : tuple[str, ...] = ('username', 'email', 'first_name', 'last_name')
