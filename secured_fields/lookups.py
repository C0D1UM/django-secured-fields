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


class EncryptedIn(lookups.In):

    def get_rhs_op(self, connection, rhs):  # pylint: disable=unused-argument
        return lookups.EndsWith(self.lhs, '%s').get_rhs_op(connection, '%s')

    def as_sql(self, compiler, connection):
        sql, params = super().as_sql(compiler, connection)

        # reformat to multiple OR condition instead
        sql += (' OR ' + sql) * (len(params) - 1)

        # search using hash for each item
        params = [
            '%' + mixins.EncryptedMixin.separator + hashlib.sha256(str(param).encode()).hexdigest()
            for param in params
        ]

        return sql, params
