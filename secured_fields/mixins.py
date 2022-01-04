__all__ = [
    'EncryptedMixin',
    'DateMixin',
]

import typing

from cryptography import fernet
from django.utils.functional import cached_property

from .fernet import get_fernet


class EncryptedMixin(object):
    """Mixin for encrypting/decrypting field value"""

    _encrypted_internal_type = 'BinaryField'
    internal_type = _encrypted_internal_type

    def get_internal_type(self):
        return self.internal_type

    def get_original_internal_type(self):
        return super().get_internal_type()

    def prepare_string(self, value) -> str:
        return str(value)

    def prepare_encryption(self, value) -> bytes:
        return self.prepare_string(value).encode()

    def get_prep_value(self, value):
        if value is None:
            return value

        value = super().get_prep_value(value)
        value = self.prepare_encryption(value)
        return get_fernet().encrypt(value)

    def decrypt(self, value: bytes) -> typing.Union[bytes, str]:
        value = get_fernet().decrypt(value)

        # convert to str if not expecting bytes
        if super().get_internal_type() != 'BinaryField':
            value = value.decode()

        return value

    def from_db_value(self, value: memoryview, expression, connection):  # pylint: disable=unused-argument
        if value is None:
            return value

        return self.to_python(value.tobytes())

    def to_python(self, value):
        if value is None:
            return value

        if not isinstance(value, bytes):
            return value

        try:
            value = self.decrypt(value)
        except fernet.InvalidToken:
            pass

        return super().to_python(value)

    @cached_property
    def validators(self):
        """Correcting internal type using for validation in integer-based fields"""
        self.internal_type = super().get_internal_type()
        results = super().validators
        self.internal_type = self._encrypted_internal_type

        return results


class DateMixin(object):

    def prepare_string(self, value) -> str:
        return value.isoformat()
