from django.urls import path
from .views import DashboardView, StartTicketView, TicketDetailView, TicketReportView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('reportes/', TicketReportView.as_view(), name='ticket_report'),
    path('tickets/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
    path('tickets/<int:pk>/iniciar/', StartTicketView.as_view(), name='start_ticket'),
]
