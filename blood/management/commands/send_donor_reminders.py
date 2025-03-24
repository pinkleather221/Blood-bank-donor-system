# management/commands/send_donor_reminders.py

from django.core.management.base import BaseCommand
from blood.tasks import send_eligible_donor_reminders

class Command(BaseCommand):
    help = 'Send reminder emails to eligible donors'

    def handle(self, *args, **options):
        self.stdout.write('Sending donor reminders...')
        send_eligible_donor_reminders()
        self.stdout.write(self.style.SUCCESS('Successfully sent donor reminders'))