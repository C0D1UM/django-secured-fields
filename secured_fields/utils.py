import hashlib
import typing

from django.conf import settings


def hash_with_salt(value: typing.Union[str, bytes]) -> str:
    if isinstance(value, str):
        value = value.encode()

    salt = getattr(settings, 'SECURED_FIELDS_HASH_SALT', '').encode()

    return hashlib.sha256(value + salt).hexdigest()
