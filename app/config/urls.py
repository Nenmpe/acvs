
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
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
    # Also expose non-namespaced auth URLs so default templates can reverse them
    path('accounts/password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html'
         ),
         name='password_reset'),
    path('accounts/password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('accounts/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('credentials/', include('credentials.urls')), # For issuing, uploading and downloading credentials or PDF
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)