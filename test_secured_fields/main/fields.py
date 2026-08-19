__all__ = [
    'EncryptedBigIntegerField',
    'EncryptedUUIDField',
]

from django.db import models

import secured_fields
from secured_fields import lookups


class EncryptedBigIntegerField(secured_fields.EncryptedMixin, models.BigIntegerField):
    """Custom field making sure `EncryptedMixin` supports every integer-based field"""


class EncryptedUUIDField(secured_fields.EncryptedMixin, models.UUIDField):
    """Custom field from the `EncryptedMixin` example in the README"""


EncryptedBigIntegerField.register_lookup(lookups.EncryptedExact, 'exact')
EncryptedBigIntegerField.register_lookup(lookups.EncryptedIn, 'in')
EncryptedUUIDField.register_lookup(lookups.EncryptedExact, 'exact')
EncryptedUUIDField.register_lookup(lookups.EncryptedIn, 'in')
