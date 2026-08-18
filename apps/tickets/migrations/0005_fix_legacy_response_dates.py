from django.db import migrations


def restore_legacy_response_dates(apps, schema_editor):
    Ticket = apps.get_model('tickets', 'Ticket')
    TicketResponse = apps.get_model('tickets', 'TicketResponse')

    for ticket in Ticket.objects.exclude(admin_notes='').exclude(admin_notes__isnull=True):
        TicketResponse.objects.filter(
            ticket_id=ticket.pk,
            message=ticket.admin_notes,
        ).update(created_at=ticket.updated_at)


class Migration(migrations.Migration):
    dependencies = [
        ('tickets', '0004_backfill_ticket_responses'),
    ]

    operations = [
        migrations.RunPython(restore_legacy_response_dates, migrations.RunPython.noop),
    ]
