from django.contrib import admin

from apps.tickets.models import TicketType


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'currency', 'is_popular', 'is_active', 'sort_order')
    list_filter = ('currency', 'is_active', 'is_popular')
    list_editable = ('is_active', 'is_popular', 'sort_order')
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'id')
