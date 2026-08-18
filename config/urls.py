"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from types import MethodType


def root_redirect(request):
    """Direct root traffic straight to login (or dashboard if already authenticated)."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def restricted_admin_permission(self, request):
    """Allow the Django admin only to real administrators, not TI staff."""
    return (
        request.user.is_active
        and request.user.is_authenticated
        and (request.user.is_superuser or request.user.role == 'ADMIN')
    )


admin.site.has_permission = MethodType(restricted_admin_permission, admin.site)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect, name='home'),
    path('', root_redirect, name='root'),
    path('', include('apps.accounts.urls')),
    path('', include('apps.tickets.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
