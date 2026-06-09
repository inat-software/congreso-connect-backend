from django.contrib import admin

from apps.tickets.models import Order, TicketType


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'currency', 'is_popular', 'is_active', 'sort_order')
    list_filter = ('currency', 'is_active', 'is_popular')
    list_editable = ('is_active', 'is_popular', 'sort_order')
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'id')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket_type_name', 'user', 'quantity', 'total_amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency')
    search_fields = ('ticket_type_name', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    ordering = ('-created_at',)
