from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {
            "fields": ("role", "university"),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Custom Fields", {
            "fields": ("role", "university"),
        }),
    )

    list_display = ("username", "email", "role", "university", "is_staff", "is_active")
    list_filter = ("role", "university", "is_staff")