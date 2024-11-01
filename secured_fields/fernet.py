import typing

from cryptography import fernet
from django.conf import settings

fernet_client: typing.Optional[fernet.MultiFernet] = None


def get_fernet():
    global fernet_client

    if fernet_client is None:
        fernet_key = getattr(settings, 'SECURED_FIELDS_KEY', None)
        assert fernet_key is not None, '`SECURED_FIELDS_KEY` is required when using django-secured-fields'

        if isinstance(fernet_key, str):
            fernet_keys = [fernet_key]
        else:
            fernet_keys = fernet_key

        fernet_instances = [fernet.Fernet(key) for key in fernet_keys]
        fernet_client = fernet.MultiFernet(fernet_instances)

    return fernet_client
