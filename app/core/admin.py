from django.contrib import admin # noqa
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # noqa
from django.utils.translation import gettext_lazy as _
from core import models # noqa


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']

    fieldsets = (

        (_('Credentials'), {'fields': ('email', 'password')}),
        (_('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (_('Add user'), {  # 'classes': ('wide',),
                         'fields': ('email',
                                    'password1',
                                    'password2',
                                    'name',
                                    'is_active',
                                    'is_staff',
                                    'is_superuser')}),

    )


admin.site.register(models.User, UserAdmin)
