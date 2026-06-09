from django.contrib import admin

from apps.stands.models import StandReservation, StandType


@admin.register(StandType)
class StandTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'dimensions', 'price', 'currency', 'is_active', 'sort_order')
    list_filter = ('currency', 'is_active')
    list_editable = ('is_active', 'sort_order')
    search_fields = ('name', 'dimensions')
    ordering = ('sort_order', 'id')


@admin.register(StandReservation)
class StandReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'stand_type_name', 'user', 'quantity', 'total_amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency')
    search_fields = ('stand_type_name', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    ordering = ('-created_at',)
