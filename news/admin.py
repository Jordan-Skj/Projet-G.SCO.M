from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import News


@admin.register(News)
class NewsAdmin(ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'is_featured', 'display_order', 'published_at')
    list_filter = ('is_published', 'is_featured', 'category', 'published_at')
    search_fields = ('title', 'summary', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-published_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_published', 'is_featured')
