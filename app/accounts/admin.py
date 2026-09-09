from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AuditLog, Student, UniversityAdmin, User, Verifier


class UniversityScopedAdminMixin:
    def _is_university_admin(self, request):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "UNIVERSITY_ADMIN"
        )

    def has_module_permission(self, request):
        if self._is_university_admin(request):
            return True
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        if self._is_university_admin(request):
            return True
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if self._is_university_admin(request):
            return obj is None or getattr(obj, "university_id", None) == request.user.university_id
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        if self._is_university_admin(request):
            return True
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if self._is_university_admin(request):
            return False
        return super().has_delete_permission(request, obj)


class RoleUserAdmin(UniversityScopedAdminMixin, UserAdmin):
    role = None
    fieldsets = UserAdmin.fieldsets + (
        ("University", {"fields": ("university", "course")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("University", {"fields": ("university", "course")}),
    )
    list_display = ("username", "email", "university", "is_staff", "is_active")
    list_filter = ("university", "is_staff", "is_active")

    def get_list_filter(self, request):
        if self._is_university_admin(request):
            return ("is_staff", "is_active")

        base = super().get_list_filter(request)
        if not getattr(request.user, "is_superuser", False):
            if base:
                try:
                    return tuple(f for f in base if f != "university")
                except TypeError:
                    return base
        return base

    def get_queryset(self, request):
        queryset = super().get_queryset(request).filter(role=self.role)
        if self._is_university_admin(request):
            queryset = queryset.filter(university=request.user.university)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "university" and self._is_university_admin(request):
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                id=request.user.university_id
            )
        if db_field.name == "course" and self._is_university_admin(request):
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                university=request.user.university
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "email" and self.role in {"STUDENT", "VERIFIER"}:
            formfield.required = True
        return formfield

    def save_model(self, request, obj, form, change):
        obj.role = self.role
        if self._is_university_admin(request):
            obj.university = request.user.university
        super().save_model(request, obj, form, change)


@admin.register(Student)
class StudentAdmin(RoleUserAdmin):
    role = "STUDENT"
    
    def has_view_permission(self, request, obj=None):
        if getattr(request.user, "role", None) == "UNIVERSITY_ADMIN":
            return True
        if request.user.is_superuser:
            return True
        return super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        if getattr(request.user, "role", None) == "UNIVERSITY_ADMIN":
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if getattr(request.user, "role", None) == "UNIVERSITY_ADMIN":
            return obj is None or getattr(obj, "university_id", None) == request.user.university_id
        return False

    def has_delete_permission(self, request, obj=None):
        if getattr(request.user, "role", None) == "UNIVERSITY_ADMIN":
            return obj is None or getattr(obj, "university_id", None) == request.user.university_id
        return False


@admin.register(UniversityAdmin)
class UniversityAdminAdmin(RoleUserAdmin):
    role = "UNIVERSITY_ADMIN"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if self._is_university_admin(request):
            return queryset.filter(id=request.user.id)
        return queryset

    def has_add_permission(self, request):
        if self._is_university_admin(request):
            return False
        return super().has_add_permission(request)

    def has_module_permission(self, request):
        if self._is_university_admin(request):
            return False
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        if self._is_university_admin(request):
            return False
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if self._is_university_admin(request):
            return False
        return super().has_change_permission(request, obj)


@admin.register(Verifier)
class VerifierAdmin(RoleUserAdmin):
    role = "VERIFIER"
    fieldsets = UserAdmin.fieldsets
    add_fieldsets = UserAdmin.add_fieldsets
    list_display = ("username", "email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")

    def get_queryset(self, request):
        queryset = UserAdmin.get_queryset(self, request).filter(role=self.role)
        if self._is_university_admin(request):
            return queryset.none()
        return queryset

    def has_module_permission(self, request):
        if self._is_university_admin(request):
            return False
        return super().has_module_permission(request)


# @admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("role", "university")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Custom Fields", {"fields": ("role", "university")}),
    )
    list_display = ("username", "email", "role", "university", "is_staff", "is_active")
    list_filter = ("role", "university", "is_staff")

    def has_module_permission(self, request):
        if getattr(request.user, "role", None) == "UNIVERSITY_ADMIN":
            return False
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        if getattr(request.user, "role", None) == "UNIVERSITY_ADMIN":
            return False
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if getattr(request.user, "role", None) == "UNIVERSITY_ADMIN":
            return False
        return super().has_change_permission(request, obj)

    def has_add_permission(self, request):
        if getattr(request.user, "role", None) == "UNIVERSITY_ADMIN":
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if getattr(request.user, "role", None) == "UNIVERSITY_ADMIN":
            return False
        return super().has_delete_permission(request, obj)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    # list_display = ("user", "action", "student_id", "credential_id", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("description", "user__username")
    
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if getattr(request.user, "role", None) == "UNIVERSITY_ADMIN":
            return queryset.filter(user__university=request.user.university)
        return queryset

    def has_module_permission(self, request):
        if getattr(request.user, "role", None) == "UNIVERSITY_ADMIN":
            return False
        return super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        if getattr(request.user, "role", None) == "UNIVERSITY_ADMIN":
            return False
        return super().has_view_permission(request, obj)
    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def get_actions(self, request):
        actions = super().get_actions(request) or {}
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions
