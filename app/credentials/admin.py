from django.contrib import admin

from accounts.models import User
from .models import Credential


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "university",
        "degree_name",
        "field_of_study",
        "issue_date",
        "is_revoked",
    )
    list_filter = ("university", "is_revoked", "issue_date")
    search_fields = (
        "student__username",
        "student__email",
        "degree_name",
        "field_of_study",
        "credential_id",
    )

    def _is_university_admin(self, request):
        return getattr(request.user, "role", None) == "UNIVERSITY_ADMIN"

    def get_list_filter(self, request):
        if self._is_university_admin(request):
            return ("is_revoked", "issue_date")

        base = super().get_list_filter(request)
        if not getattr(request.user, "is_superuser", False):
            if base:
                try:
                    return tuple(f for f in base if f != "university")
                except TypeError:
                    return base
        return base

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if self._is_university_admin(request):
            return queryset.filter(
                university=request.user.university,
                student__university=request.user.university,
            )
        return queryset

    def has_module_permission(self, request):
        if self._is_university_admin(request):
            return True
        return super().has_module_permission(request)

    def has_add_permission(self, request):
        if self._is_university_admin(request):
            return True
        if request.user.is_superuser:
            return False
        return super().has_add_permission(request)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if self._is_university_admin(request):
            if db_field.name == "university":
                kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                    id=request.user.university_id
                )
            elif db_field.name == "student":
                kwargs["queryset"] = User.objects.filter(
                    role="STUDENT",
                    university=request.user.university,
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if self._is_university_admin(request):
            obj.university = request.user.university
        super().save_model(request, obj, form, change)

    def has_view_permission(self, request, obj=None):
        if self._is_university_admin(request):
            return (
                obj is None
                or (
                    obj.university_id == request.user.university_id
                    and obj.student.university_id == request.user.university_id
                )
            )
        return super().has_view_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if self._is_university_admin(request):
            return (
                obj is None
                or (
                    obj.university_id == request.user.university_id
                    and obj.student.university_id == request.user.university_id
                )
            )
        if request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if self._is_university_admin(request):
            return (
                obj is None
                or (
                    obj.university_id == request.user.university_id
                    and obj.student.university_id == request.user.university_id
                )
            )
        if request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def get_actions(self, request):
        actions = super().get_actions(request) or {}
        # prevent bulk delete for non-university-admins (including superusers)
        if not self._is_university_admin(request) and "delete_selected" in actions:
            del actions["delete_selected"]
        return actions
