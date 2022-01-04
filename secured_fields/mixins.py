__all__ = ['EncryptedMixin']

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

    def get_prep_value(self, value):
        if value is None:
            return value

        value = super().get_prep_value(value)
        value = self.prepare_string(value)
        return get_fernet().encrypt(value.encode())

    def to_python(self, value):
        if value is None:
            return value

        if not isinstance(value, bytes):
            return value

        try:
            value = get_fernet().decrypt(value).decode()
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