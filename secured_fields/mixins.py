__all__ = [
    'EncryptedMixin',
    'EncryptedStorageMixin',
]

import typing
from io import BytesIO

from cryptography import fernet
from django.core.files import File
from django.utils.functional import cached_property

from .fernet import get_fernet


class EncryptedMixin(object):
    """Mixin for encrypting/decrypting field value"""

    _encrypted_internal_type = 'BinaryField'

    internal_type = _encrypted_internal_type
    call_super_from_db_value = False

    def get_internal_type(self):
        return self.internal_type

    def get_original_internal_type(self):
        return super().get_internal_type()

    def prepare_string(self, value) -> str:
        return str(value)

    def prepare_encryption(self, value) -> bytes:
        return self.prepare_string(value).encode()

    def get_db_prep_save(self, value, connection):
        if value is None:
            return value

        if self.get_original_internal_type() != 'BinaryField':
            value = super().get_db_prep_save(value, connection)
            value = self.prepare_encryption(value)

        return get_fernet().encrypt(value)

    # def get_db_prep_value(self, value, connection, prepared=None):  # pylint: disable=unused-argument
    #     return super().get_db_prep_value(value, connection, prepared=False)

    def decrypt(self, value: bytes) -> typing.Union[bytes, str]:
        value = get_fernet().decrypt(value)

        # convert to str if not expecting bytes
        if super().get_internal_type() != 'BinaryField':
            value = value.decode()

        return value

    def from_db_value(self, value, expression, connection):  # pylint: disable=unused-argument
        if value is None:
            return value

        # postgres support
        if isinstance(value, memoryview):
            value = value.tobytes()

        value = self.to_python(value)

        if self.call_super_from_db_value:
            value = super().from_db_value(value, expression, connection)

        return value

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


class EncryptedStorageMixin(object):
    """Mixin for encrypt/decrypt file content before saving/after getting from the storage"""

    def _open(self, name, mode='rb'):
        content = super()._open(name, mode)
        decrypted_content = get_fernet().decrypt(content.read())
        return File(BytesIO(decrypted_content))

    def _save(self, name, content):
        encrypted_content = get_fernet().encrypt(content.read())
        content.seek(0)
        content.write(encrypted_content)
        content.seek(0)

        return super()._save(name, content)
