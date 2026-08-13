from django.urls import path
from .views import AzertaLoginView, AzertaLogoutView

urlpatterns = [
    path('login/', AzertaLoginView.as_view(), name='login'),
    path('logout/', AzertaLogoutView.as_view(), name='logout'),
]
