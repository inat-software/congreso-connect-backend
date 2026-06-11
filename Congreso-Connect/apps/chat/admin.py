from django.contrib import admin

from apps.chat.models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ('sender', 'body', 'read_at', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_a', 'user_b', 'last_message_at', 'created_at')
    search_fields = (
        'user_a__email', 'user_a__first_name', 'user_a__last_name',
        'user_b__email', 'user_b__first_name', 'user_b__last_name',
    )
    readonly_fields = ('created_at', 'updated_at', 'last_message_at')
    ordering = ('-last_message_at', '-created_at')
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'short_body', 'read_at', 'created_at')
    list_filter = ('read_at',)
    search_fields = ('body', 'sender__email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    @admin.display(description='mensaje')
    def short_body(self, obj):
        return (obj.body[:60] + '…') if len(obj.body) > 60 else obj.body
