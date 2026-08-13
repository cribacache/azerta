from django.urls import path
from .views import DashboardView, TicketDetailView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
]
