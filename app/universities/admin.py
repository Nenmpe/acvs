from django.contrib import admin

from .models import University, UniversityCourse


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

@admin.register(UniversityCourse)
class UniversityCourseAdmin(admin.ModelAdmin):
    list_filter = ("university",)
    search_fields = ("degree_name", "course_name", "field_of_study")

    def _is_university_admin(self, request):
        return getattr(request.user, "role", None) == "UNIVERSITY_ADMIN"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if self._is_university_admin(request):
            return queryset.filter(university=request.user.university)
        return queryset

    def save_model(self, request, obj, form, change):
        if self._is_university_admin(request):
            obj.university = request.user.university
        super().save_model(request, obj, form, change)

    def has_module_permission(self, request):
        return True

    def has_view_permission(self, request, obj=None):
        if self._is_university_admin(request):
            if obj is None:
                return True
            return obj.university_id == request.user.university_id
        return True

    def has_change_permission(self, request, obj=None):
        if self._is_university_admin(request):
            if obj is None:
                return True
            return obj.university_id == request.user.university_id
        return False

    def has_add_permission(self, request):
        if self._is_university_admin(request):
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if self._is_university_admin(request):
            if obj is None:
                return True
            return obj.university_id == request.user.university_id
        return False

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "university" and self._is_university_admin(request):
            kwargs["queryset"] = db_field.remote_field.model.objects.filter(
                id=request.user.university_id
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
