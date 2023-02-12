"""
Django admin customization
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models


class AdminUser(BaseUserAdmin):
    """Define user admin"""
    ordering = ['id']
    list_display = ['name', 'email']
    fieldsets = [
        [None, {'fields': ['name', 'email']}],
        [_('Permissions'),
         {'fields':
            [
                'is_active',
                'is_superuser',
                'is_staff'
            ]
          }
         ],
        [_('Important Dates'), {'fields': ['last_login']}]
    ]
    readonly_fields = ['last_login']
    add_fieldsets = [
        [None, {
            'classes': ['wide'],
            'fields': [
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser'
            ]
        }
        ],
    ]


admin.site.register(models.User, AdminUser)
