__all__ = ['EncryptedMixin']

from cryptography import fernet

from .fernet import get_fernet


class EncryptedMixin(object):
    """Mixin for encrypting/decrypting field value"""

    def get_internal_type(self):
        return 'BinaryField'

    def prepare_string(self, value) -> str:
        return str(value)

    def get_prep_value(self, value):
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
