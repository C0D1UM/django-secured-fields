import typing

from cryptography import fernet
from django.conf import settings

fernet_client: typing.Optional[fernet.Fernet] = None


def get_fernet():
    global fernet_client

    if fernet_client is None:
        fernet_key = getattr(settings, 'SECURED_FIELDS_KEY', None)
        assert fernet_key is not None, '`SECURED_FIELDS_KEY` is required when using django-secured-fields'

        fernet_client = fernet.Fernet(fernet_key)

    return fernet_client
