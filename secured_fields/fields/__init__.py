__all__ = [
    'EncryptedBinaryField',
    'EncryptedBooleanField',
    'EncryptedCharField',
    'EncryptedDateField',
    'EncryptedDateTimeField',
    'EncryptedDecimalField',
    'EncryptedFileField',
    'EncryptedImageField',
    'EncryptedIntegerField',
    'EncryptedJSONField',
    'EncryptedTextField',
]

import json

from django.db import models

from .files import *
from .. import mixins, lookups


class EncryptedBinaryField(mixins.EncryptedMixin, models.BinaryField):

    def prepare_encryption(self, value) -> bytes:
        return value


class EncryptedBooleanField(mixins.EncryptedMixin, models.BooleanField):
    pass


class EncryptedCharField(mixins.EncryptedMixin, models.CharField):
    pass


class EncryptedDateField(mixins.EncryptedMixin, models.DateField):
    pass


class EncryptedDateTimeField(mixins.EncryptedMixin, models.DateTimeField):
    pass


class EncryptedDecimalField(mixins.EncryptedMixin, models.DecimalField):
    pass


class EncryptedIntegerField(mixins.EncryptedMixin, models.IntegerField):
    pass


class EncryptedJSONField(mixins.EncryptedMixin, models.JSONField):
    call_super_from_db_value = True

    def prepare_db_value(self, value, connection):  # pylint: disable=unused-argument
        # NOTE: `JSONField.get_db_prep_value()` delegates to `connection.ops.adapt_json_value()`,
        #       which returns a driver-specific wrapper (`Jsonb`) on PostgreSQL instead of a JSON
        #       string. The value is encoded here so the encrypted payload is always the JSON text
        #       regardless of the database backend.
        return json.dumps(value, cls=self.encoder)


class EncryptedTextField(mixins.EncryptedMixin, models.TextField):
    pass


# exact
# BinaryField is not supported, JSON use special exact class
EncryptedBooleanField.register_lookup(lookups.EncryptedExact, 'exact')
EncryptedCharField.register_lookup(lookups.EncryptedExact, 'exact')
EncryptedDateField.register_lookup(lookups.EncryptedExact, 'exact')
EncryptedDateTimeField.register_lookup(lookups.EncryptedExact, 'exact')
EncryptedDecimalField.register_lookup(lookups.EncryptedExact, 'exact')
EncryptedIntegerField.register_lookup(lookups.EncryptedExact, 'exact')
EncryptedJSONField.register_lookup(lookups.EncryptedJSONExact, 'exact')
EncryptedTextField.register_lookup(lookups.EncryptedExact, 'exact')

# in
# BinaryField and JSONField are not supported
EncryptedBooleanField.register_lookup(lookups.EncryptedIn, 'in')
EncryptedCharField.register_lookup(lookups.EncryptedIn, 'in')
EncryptedDateField.register_lookup(lookups.EncryptedIn, 'in')
EncryptedDateTimeField.register_lookup(lookups.EncryptedIn, 'in')
EncryptedDecimalField.register_lookup(lookups.EncryptedIn, 'in')
EncryptedIntegerField.register_lookup(lookups.EncryptedIn, 'in')
EncryptedTextField.register_lookup(lookups.EncryptedIn, 'in')
