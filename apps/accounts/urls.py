from django.urls import path
from .views import (
    AzertaLoginView,
    AzertaLogoutView,
    user_create,
    user_delete,
    dismiss_onboarding,
    user_list,
    user_update,
)

urlpatterns = [
    path('login/', AzertaLoginView.as_view(), name='login'),
    path('logout/', AzertaLogoutView.as_view(), name='logout'),
    path('usuarios/', user_list, name='user_list'),
    path('usuarios/nuevo/', user_create, name='user_create'),
    path('usuarios/<int:pk>/editar/', user_update, name='user_update'),
    path('usuarios/<int:pk>/eliminar/', user_delete, name='user_delete'),
    path('guia/no-mostrar/', dismiss_onboarding, name='dismiss_onboarding'),
]
