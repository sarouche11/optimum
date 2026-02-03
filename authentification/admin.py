from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Profile

@admin.register(Profile)
class ProfileImportExport(ImportExportModelAdmin):
    fields = [
        'user',
        'adresse',
        'phone',
        'active',
    ]

    readonly_fields = [
        'get_username',
        'get_first_name',
        'get_last_name',
        'get_email',
    ]

    list_display = [
        'codeU',
        'get_username',
        'get_first_name',
        'get_last_name',
        'get_email',
        'adresse',
        'phone',
        'active',
        'created_at',
        'updated_at',
    ]

    search_fields = ['user__username', 'user__email', 'codeU']
    list_filter = ['active']

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'