from django.contrib import admin

from .models import University


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "website", "created_at")
    search_fields = ("name", "email")

    def _is_university_admin(self, request):
        return getattr(request.user, "role", None) == "UNIVERSITY_ADMIN"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if self._is_university_admin(request):
            return queryset.filter(id=request.user.university_id)
        return queryset

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

    def has_add_permission(self, request):
        if self._is_university_admin(request):
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if self._is_university_admin(request):
            return False
        return super().has_delete_permission(request, obj)
