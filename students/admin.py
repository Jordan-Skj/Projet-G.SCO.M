from django.contrib import admin
from unfold.admin import UnfoldAdmin
from .models import AcademicYear, SchoolClass, Student

# Register your models here.
@admin.register(AcademicYear)
class AcademicYearAdmin(UnfoldAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('name',)
    
@admin.register(SchoolClass)
class SchoolClassAdmin(UnfoldAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    
@admin.register(Student)
class StudentAdmin(UnfoldAdmin):
    list_display = ('admission_number', 'first_name', 'middle_name', 'last_name', 'gender', 'status', 'created_at', 'updated_at')
    list_filter = ('gender', 'status', 'created_at', 'updated_at')
    search_fields = ('admission_number', 'first_name', 'middle_name', 'last_name')
    ordering = ('last_name', 'middle_name', 'first_name')
    