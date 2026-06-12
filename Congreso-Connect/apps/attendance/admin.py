from django.contrib import admin

from apps.attendance.models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'dni', 'method', 'user', 'registered_by', 'created_at',
    )
    list_filter = ('method',)
    search_fields = ('first_name', 'last_name', 'dni', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
