from django.contrib import admin

from apps.stands.models import StandType


@admin.register(StandType)
class StandTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'dimensions', 'price', 'currency', 'is_active', 'sort_order')
    list_filter = ('currency', 'is_active')
    list_editable = ('is_active', 'sort_order')
    search_fields = ('name', 'dimensions')
    ordering = ('sort_order', 'id')
