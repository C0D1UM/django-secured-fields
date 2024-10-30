__all__ = [
    'EncryptedMixin',
    'EncryptedStorageMixin',
]

import typing
from io import BytesIO

from cryptography import fernet
from django.core.files import File
from django.db import connection
from django.db.models import Field
from django.utils.functional import cached_property

from . import exceptions, utils
from .enum import DatabaseVendor
from .fernet import get_fernet


class EncryptedMixin(Field):
    """Mixin for encrypting/decrypting field value"""

    _encrypted_internal_type = 'TextField'
    separator = '$'

    internal_type = _encrypted_internal_type
    call_super_from_db_value = False

    def __init__(self, *args, searchable=False, **kwargs):
        if self.get_original_internal_type() == 'BinaryField' and searchable:
            raise NotImplementedError('`BinaryField` with `searchable=True` is not supported yet')
        self.searchable = searchable

        kwargs['unique'] = False
        if self.searchable:
            # NOTE: MySQL does not support index on `longtext` column
            if connection.vendor != DatabaseVendor.MYSQL:
                kwargs['db_index'] = True

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()

        if self.searchable is not False:
            kwargs['searchable'] = self.searchable

        kwargs.pop('unique', None)
        if self.searchable:
            kwargs.pop('db_index', None)

        return name, path, args, kwargs

    def get_internal_type(self):
        return self.internal_type

    def get_original_internal_type(self):
        return super().get_internal_type()

    def prepare_string(self, value) -> str:
        return str(value)

    def prepare_encryption(self, value) -> bytes:
        return self.prepare_string(value).encode()

    def get_db_prep_save(self, value, connection):  # pylint: disable=redefined-outer-name
        if value is None:
            return value

        if not isinstance(value, bytes):
            value = super().get_db_prep_save(value, connection)

        value = self.prepare_encryption(value)

        encrypted = get_fernet().encrypt(value).decode()
        if not self.searchable:
            return encrypted

        # append hashed value
        return encrypted + self.separator + utils.hash_with_salt(value)

    def decrypt(self, value: str) -> typing.Union[bytes, str]:
        value = get_fernet().decrypt(value.encode())

        # convert to str if not expecting bytes
        if self.get_original_internal_type() != 'BinaryField':
            value = value.decode()

        return value

    def from_db_value(self, value, expression, connection):  # pylint: disable=redefined-outer-name
        if value is None:
            return value

        value = self.to_python(value)

        if self.call_super_from_db_value:
            value = super().from_db_value(value, expression, connection)

        return value

    def to_python(self, value):
        if not isinstance(value, str):
            return value

        encrypted_value = value
        if self.searchable:
            # get only encrypted section
            encrypted_value = value[:-(64 + len(self.separator))]

        try:
            value = self.decrypt(encrypted_value)
        except fernet.InvalidToken:
            # not encrypted
            pass

        return super().to_python(value)

    @cached_property
    def validators(self):
        """Correcting internal type using for validation in integer-based fields"""
        self.internal_type = super().get_internal_type()
        results = super().validators
        self.internal_type = self._encrypted_internal_type

        return results

    def get_lookup(self, lookup_name: str):
        # BinaryField is not supported (except `isnull`)
        if self.get_original_internal_type() == 'BinaryField' and lookup_name != 'isnull':
            raise exceptions.LookupNotSupported(self.get_original_internal_type(), lookup_name)

        # JSONField not supports `in`
        if self.get_original_internal_type() == 'JSONField' and lookup_name == 'in':
            raise exceptions.LookupNotSupported(self.get_original_internal_type(), lookup_name)

        allowed_lookups = ['exact', 'in', 'isnull']
        if lookup_name in allowed_lookups:
            return super().get_lookup(lookup_name)

        raise exceptions.LookupNotSupported(self.get_original_internal_type(), lookup_name)


class EncryptedStorageMixin:
    """Mixin for encrypt/decrypt file content before saving/after getting from the storage"""

    def _open(self, name, mode='rb'):
        content = super()._open(name, mode)
        decrypted_content = get_fernet().decrypt(content.read())
        return File(BytesIO(decrypted_content))

    def _save(self, name, content):
        pos = content.tell()
        content.seek(0)
        encrypted_content = get_fernet().encrypt(content.read())
        content.seek(0)
        content.write(encrypted_content)
        content.seek(pos)

        return super()._save(name, content)
