from django.db import migrations


def copy_legacy_notes_to_history(apps, schema_editor):
    Ticket = apps.get_model('tickets', 'Ticket')
    TicketResponse = apps.get_model('tickets', 'TicketResponse')

    for ticket in Ticket.objects.exclude(admin_notes='').exclude(admin_notes__isnull=True):
        if not TicketResponse.objects.filter(ticket_id=ticket.pk).exists():
            TicketResponse.objects.create(
                ticket_id=ticket.pk,
                author_id=ticket.assigned_to_id,
                message=ticket.admin_notes,
                created_at=ticket.updated_at,
            )

class Migration(migrations.Migration):
    dependencies = [
        ('tickets', '0003_ticketresponse'),
    ]

    operations = [
        migrations.RunPython(copy_legacy_notes_to_history, migrations.RunPython.noop),
    ]
