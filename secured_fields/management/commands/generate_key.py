from cryptography import fernet
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Command to generate a new Fernet key'

    def handle(self, *args, **options):  # pylint: disable=unused-argument
        print(fernet.Fernet.generate_key().decode())
