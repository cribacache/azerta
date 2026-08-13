from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'priority', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('title', 'description', 'created_by__username', 'created_by__email')
    readonly_fields = ('created_at', 'updated_at')
