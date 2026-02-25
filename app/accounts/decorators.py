from django.core.exceptions import PermissionDenied

def university_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        
        if request.user.role != "UNIVERSITY_ADMIN":
            raise PermissionDenied
        
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        
        if request.user.role != "STUDENT":
            raise PermissionDenied
        
        return view_func(request, *args, **kwargs)
    return wrapper