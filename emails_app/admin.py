from django.contrib import admin

from emails_app.models import Client, EmailRecord, SMTPSettings
from emails_app.utils import truncate_string


@admin.register(SMTPSettings)
class SMTPSettingsAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'username', 'use_tls', 'use_ssl')
    fieldsets = (
        (None, {
            'fields': ('host', 'username', 'password', 'default_from_email')
        }),
        ('Security', {
            'fields': ('use_tls', 'use_ssl'),
            'description': 'Configure security settings for the SMTP connection. The port will be set automatically.'
        }),
    )

    def has_add_permission(self, request):
        # Only allow adding if there are no existing settings
        return not SMTPSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Disable delete permission
        return False


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('system_name', 'static_ip',)
    search_fields = ('system_name', 'static_ip', 'user__username')


@admin.register(EmailRecord)
class EmailRecordAdmin(admin.ModelAdmin):
    list_display = ('client', 'short_subject', 'short_recipient',
                    'status', 'task_type', 'timestamp', 'error_message',)
    list_filter = ['status', 'client']
    list_per_page = 50
    readonly_fields = ('client', 'subject', 'recipient',
                       'status', 'task_type', 'timestamp', 'error_message')

    def has_add_permission(self, request):
        return False  # Disable add permission

    def has_change_permission(self, request, obj=None):
        return False  # Disable change permission

    def has_delete_permission(self, request, obj=None):
        return False  # Disable delete permission

    @admin.display(description='Subject')
    def short_subject(self, obj):
        return truncate_string(obj, field_name='subject', max_length=150)

    @admin.display(description='Recipient')
    def short_recipient(self, obj):
        return truncate_string(obj, field_name='recipient', max_length=150)
