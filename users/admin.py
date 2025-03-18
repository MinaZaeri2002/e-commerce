import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.contrib.auth.forms import UserCreationForm

logger = logging.getLogger('users')


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('phone_number', 'email', 'username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            username = self.cleaned_data.get('phone_number')
        return username


class MyUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    model = User
    list_display = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'is_staff', 'is_admin')
    search_fields = ('first_name', 'last_name')
    ordering = ('username', 'first_name', 'last_name', 'phone_number', 'is_staff')

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            if request.user.is_superuser:
                return (
                    (None, {
                        'classes': ('wide',),
                        'fields': ('email', 'first_name', 'last_name', 'phone_number', 'username', 'password1', 'password2', 'is_staff', 'is_admin', 'is_superuser'),
                    }),
                )
            elif request.user.is_admin:
                return (
                    (None, {
                        'classes': ('wide',),
                        'fields': ('email', 'first_name', 'last_name', 'phone_number', 'username', 'password1', 'password2', 'is_staff', 'is_admin'),
                    }),
                )
            else:
                return (
                    (None, {
                        'classes': ('wide',),
                        'fields': ('email', 'first_name', 'last_name', 'phone_number', 'username', 'password1', 'password2', 'is_staff'),
                    }),
                )
        else:
            if request.user.is_superuser:
                return (
                    (None, {'fields': ('username', 'password')}),
                    ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'is_staff', 'is_admin', 'is_superuser')}),
                    ('Important dates', {'fields': ('date_joined',)}),
                )
            elif request.user.is_admin:
                return (
                    (None, {'fields': ('username', 'password')}),
                    ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'is_staff', 'is_admin')}),
                    ('Important dates', {'fields': ('date_joined',)}),
                )
            else:
                return (
                    (None, {'fields': ('username', 'password')}),
                    ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
                    ('Important dates', {'fields': ('date_joined',)}),
                )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_staff and not request.user.is_superuser:
            qs = qs.filter(is_superuser=False)
        return qs

    def has_module_permission(self, request):
        return request.user.is_active and (request.user.is_staff or request.user.is_superuser or request.user.is_admin)

    def has_add_permission(self, request):
        return request.user.is_staff or request.user.is_admin

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.is_superuser:
            logger.warning(f"Admin {request.user.username} attempted to modify superuser: {obj.username}")
            return False
        if request.user.is_staff:
            return True

        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj and obj.is_superuser:
            logger.warning(f"Admin {request.user.username} attempted to delete superuser: {obj.username}")
            return False
        if request.user.is_admin:
            return True

        return super().has_delete_permission(request, obj)

    def delete_button(self, obj):
        if obj is not None:
            logger.info(f"Admin {self.request.user.username} accessed delete button for user: {obj.username}")
        return format_html(
            '<a class="button" href="{}?delete=True">Delete</a>',
            obj.id
        )
    delete_button.short_description = 'Delete'

    @admin.action(description='Delete selected users')
    def delete_user(self, request, queryset):
        if not request.user.is_superuser:
            queryset = queryset.filter(is_superuser=False)
        queryset.delete()

    actions = ['delete_user']


admin.site.unregister(Group)
admin.site.register(User, MyUserAdmin)