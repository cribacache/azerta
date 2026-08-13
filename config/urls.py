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


def root_redirect(request):
    """Direct root traffic straight to login (or dashboard if already authenticated)."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect, name='home'),
    path('', root_redirect, name='root'),
    path('', include('apps.accounts.urls')),
    path('', include('apps.tickets.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
