import hashlib
import json

from django.db.models import lookups

from . import mixins


class EncryptedExact(lookups.EndsWith):

    def as_sql(self, compiler, connection):
        sql, params = super().as_sql(compiler, connection)

        # search using hash
        hashed = hashlib.sha256(params[0][1:].encode()).hexdigest()
        params[0] = '%' + mixins.EncryptedMixin.separator + hashed

        return sql, params


class EncryptedJSONExact(EncryptedExact):

    def get_db_prep_lookup(self, value, connection):
        value = json.dumps(value)

        return super().get_db_prep_lookup(value, connection)
