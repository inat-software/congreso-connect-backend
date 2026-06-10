from django.contrib import admin

from apps.content.models import EventConfig, Speaker, Sponsor


@admin.register(EventConfig)
class EventConfigAdmin(admin.ModelAdmin):
    """Singleton: una sola fila de configuración del evento."""

    def has_add_permission(self, request):
        return not EventConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'topic', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'sort_order')
    search_fields = ('name', 'role', 'position', 'topic')
    ordering = ('sort_order', 'id')


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'website', 'is_active', 'sort_order')
    list_filter = ('is_active', 'tier')
    list_editable = ('is_active', 'sort_order')
    search_fields = ('name', 'tier')
    ordering = ('sort_order', 'id')
