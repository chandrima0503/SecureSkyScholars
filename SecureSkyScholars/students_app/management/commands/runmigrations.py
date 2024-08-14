from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Run database migrations'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting migrations...'))
        call_command('migrate')
        self.stdout.write(self.style.SUCCESS('Migrations completed!'))
