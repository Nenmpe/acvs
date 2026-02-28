
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from base.views import logout as jwt_logout


urlpatterns = [
    # Override admin logout so JWT cookies are cleared when logging out from the admin panel
    path('admin/logout/', jwt_logout),
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('credential/', include('verification.urls')), # For verifying the credential
    path('accounts/', include('accounts.urls')),
    path('credentials/', include('credentials.urls')), # For issuing, uploading and downloading credentials or PDF
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)