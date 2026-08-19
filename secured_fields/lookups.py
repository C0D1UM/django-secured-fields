import json

from django.db.models import lookups

from . import mixins, utils


class EncryptedExact(lookups.EndsWith):

    def process_rhs(self, qn, connection):
        # NOTE: `PatternLookup.process_rhs()` is intentionally skipped here. It escapes LIKE
        #       wildcards (`%`, `_` and `\`) in the value which would make the hash differ
        #       from the one stored alongside the encrypted value.
        rhs, params = lookups.Lookup.process_rhs(self, qn, connection)

        if self.rhs_is_direct_value() and params and not self.bilateral_transforms:
            # search using hash
            params[0] = '%' + mixins.EncryptedMixin.separator + utils.hash_with_salt(str(params[0]))

        return rhs, params


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
        sql = f'({sql})'

        # search using hash for each item
        params = [
            '%' + mixins.EncryptedMixin.separator + utils.hash_with_salt(str(param))
            for param in params
        ]

        return sql, params
