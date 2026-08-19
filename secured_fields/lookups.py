from django.db.models import lookups

from . import mixins, utils


class EncryptedExact(lookups.EndsWith):

    def get_db_prep_lookup(self, value, connection):
        # NOTE: `process_rhs()` replaces the param with its hash, so the value has to be
        #       prepared exactly the way the field prepared it when the value was saved.
        #       Some fields store a value differing from `str(value)`, e.g. `UUIDField` uses
        #       the hex form on backends without a native UUID type.
        return '%s', [self.lhs.output_field.prepare_db_value(value, connection)]

    def process_rhs(self, qn, connection):
        # NOTE: `PatternLookup.process_rhs()` is intentionally skipped here. It escapes LIKE
        #       wildcards (`%`, `_` and `\`) in the value which would make the hash differ
        #       from the one stored alongside the encrypted value.
        rhs, params = lookups.Lookup.process_rhs(self, qn, connection)

        if self.rhs_is_direct_value() and params and not self.bilateral_transforms:
            # NOTE: Django 6.0+ returns an immutable sequence of params, so a mutable copy is
            #       required before replacing the value with its hash.
            params = list(params)

            # search using hash
            params[0] = '%' + mixins.EncryptedMixin.separator + utils.hash_with_salt(str(params[0]))

        return rhs, params


class EncryptedJSONExact(EncryptedExact):
    """Kept for backward compatibility

    `EncryptedJSONField.prepare_db_value()` already encodes the value into its JSON
    representation, so no extra handling is needed here.
    """


class EncryptedIn(lookups.In):

    def get_db_prep_lookup(self, value, connection):
        # NOTE: `In.get_db_prep_lookup()` cannot be reused since it hands every value over to
        #       the field's `get_db_prep_value()`, which breaks on encrypted integer fields
        #       because their column is a text one. `as_sql()` replaces the params with their
        #       hashes anyway, so each value only needs the same preparation as when saved.
        field = self.lhs.output_field

        return '%s', [field.prepare_db_value(item, connection) for item in value]

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
