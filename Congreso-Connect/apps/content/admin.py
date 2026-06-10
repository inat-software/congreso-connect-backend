from django.contrib import admin

from apps.content.models import Speaker


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'topic', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'sort_order')
    search_fields = ('name', 'role', 'position', 'topic')
    ordering = ('sort_order', 'id')
