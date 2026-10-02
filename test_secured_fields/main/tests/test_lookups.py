import datetime
import decimal
import typing

from django import test
from django.db import connection
from django.db.models import Q

from main import models
from main.tests import utils as test_utils
from secured_fields import exceptions, lookups
from secured_fields.enum import DatabaseVendor


@test.override_settings(SECURED_FIELDS_HASH_SALT='test')
class EncryptedExactLookupTestCase(test.TestCase):

    def create_and_assert(self, model, create_value, assert_value: typing.Any = test_utils.NoValue):
        created_pk = model.objects.create(field=create_value).pk

        if assert_value is test_utils.NoValue:
            assert_value = create_value
        model = model.objects.filter(field=assert_value).first()

        self.assertIsNotNone(model)
        self.assertEqual(model.pk, created_pk)

    def assert_no_lookup(self, model, assert_value: typing.Any):
        self.assertRaises(exceptions.LookupNotSupported, model.objects.filter, field=assert_value)

    def test_binary_field(self):
        self.assert_no_lookup(models.BinaryFieldModel, b'test')

    def test_big_integer_field(self):
        self.create_and_assert(models.SearchableBigIntegerFieldModel, 2**40)

    def test_boolean_field(self):
        self.create_and_assert(models.SearchableBooleanFieldModel, True)

    def test_char_field(self):
        self.create_and_assert(models.SearchableCharFieldModel, 'test')

    def test_char_field_with_like_wildcards(self):
        """LIKE wildcards (`%`, `_`) and escape character must not affect the hashed lookup"""

        for value in ['under_score', '100%', 'back\\slash', 'mixed_10%\\value']:
            with self.subTest(value=value):
                self.create_and_assert(models.SearchableCharFieldModel, value)

    def test_date_field(self):
        self.create_and_assert(models.SearchableDateFieldModel, datetime.date(2021, 12, 31))

    def test_datetime_field(self):
        create_value = datetime.datetime(2021, 12, 31, 23, 59, 3, tzinfo=test_utils.TZ_UTC)
        assert_value = create_value

        if connection.vendor in [DatabaseVendor.MYSQL, DatabaseVendor.SQLITE]:
            assert_value = assert_value.replace(tzinfo=None)

        self.create_and_assert(models.SearchableDateTimeFieldModel, create_value, assert_value)

    def test_decimal_field(self):
        self.create_and_assert(models.SearchableDecimalFieldModel, decimal.Decimal('100.23'))

    def test_decimal_field_with_fewer_decimal_places(self):
        """The value has to be prepared the same way it was when saved (`100.2` -> `100.20`)"""

        self.create_and_assert(models.SearchableDecimalFieldModel, decimal.Decimal('100.2'))

    def test_integer_field(self):
        self.create_and_assert(models.SearchableIntegerFieldModel, 100)

    def test_json_field(self):
        self.create_and_assert(models.SearchableJSONFieldModel, {'name': 'John Doe'})

    def test_json_field_with_like_wildcards(self):
        self.create_and_assert(models.SearchableJSONFieldModel, {'name': 'John_Doe 100%'})

    def test_text_field(self):
        self.create_and_assert(models.SearchableTextFieldModel, 'test')

    def test_text_field_with_like_wildcards(self):
        self.create_and_assert(models.SearchableTextFieldModel, 'under_score 100%')

    def test_uuid_field(self):
        self.create_and_assert(models.SearchableUUIDFieldModel, test_utils.UUID_1)


@test.override_settings(SECURED_FIELDS_HASH_SALT='test')
class EncryptedInLookupTestCase(test.TestCase):

    def create_and_assert(self, model, create_value, assert_value):
        created_pk = model.objects.create(field=create_value).pk

        if not isinstance(assert_value, list):
            assert_value = [assert_value]
        model = model.objects.filter(field__in=assert_value).first()

        self.assertIsNotNone(model)
        self.assertEqual(model.pk, created_pk)

    def assert_no_lookup(self, model, assert_value: typing.Any):
        self.assertRaises(exceptions.LookupNotSupported, model.objects.filter, field__in=assert_value)

    def test_binary_field(self):
        self.assert_no_lookup(models.BinaryFieldModel, b'test')

    def test_big_integer_field(self):
        self.create_and_assert(models.SearchableBigIntegerFieldModel, 2**40, [2**40, 2**41])

    def test_boolean_field(self):
        self.create_and_assert(models.SearchableBooleanFieldModel, True, [True, False])

    def test_char_field(self):
        self.create_and_assert(models.SearchableCharFieldModel, 'test', ['test', 'user'])

    def test_char_field_with_like_wildcards(self):
        self.create_and_assert(
            models.SearchableCharFieldModel,
            'under_score 100%',
            ['under_score 100%', 'another_one'],
        )

    def test_date_field(self):
        self.create_and_assert(
            models.SearchableDateFieldModel,
            datetime.date(2021, 12, 31),
            [datetime.date(2021, 12, 31), datetime.date(2022, 2, 1)],
        )

    def test_datetime_field(self):
        create_value = datetime.datetime(2021, 12, 31, 23, 59, 3, tzinfo=test_utils.TZ_UTC)
        assert_value = [
            datetime.datetime(2021, 12, 31, 23, 59, 3, tzinfo=test_utils.TZ_UTC),
            datetime.datetime(2021, 12, 31, 23, 50, 3, tzinfo=test_utils.TZ_UTC),
        ]

        if connection.vendor in [DatabaseVendor.MYSQL, DatabaseVendor.SQLITE]:
            assert_value = list(map(lambda x: x.replace(tzinfo=None), assert_value))

        self.create_and_assert(models.SearchableDateTimeFieldModel, create_value, assert_value)

    def test_decimal_field(self):
        self.create_and_assert(
            models.SearchableDecimalFieldModel,
            decimal.Decimal('100.23'),
            [decimal.Decimal('100.23'), decimal.Decimal('10.2')],
        )

    def test_decimal_field_with_fewer_decimal_places(self):
        """Each value has to be prepared the same way it was when saved (`100.2` -> `100.20`)"""

        self.create_and_assert(
            models.SearchableDecimalFieldModel,
            decimal.Decimal('100.2'),
            [decimal.Decimal('100.2'), decimal.Decimal('10.2')],
        )

    def test_integer_field(self):
        self.create_and_assert(models.SearchableIntegerFieldModel, 100, [100, 200])

    def test_json_field(self):
        self.assert_no_lookup(models.SearchableJSONFieldModel, [{'test': 'test'}, {'john': 'doe'}])

    def test_text_field(self):
        self.create_and_assert(models.SearchableTextFieldModel, 'test', ['test', 'user'])

    def test_uuid_field(self):
        self.create_and_assert(
            models.SearchableUUIDFieldModel,
            test_utils.UUID_1,
            [test_utils.UUID_1, test_utils.UUID_2],
        )


@test.override_settings(SECURED_FIELDS_HASH_SALT='test')
class IsNullLookupTestCase(test.TestCase):

    def create_and_assert(self, model):
        created_pk = model.objects.create(field=None).pk
        model = model.objects.filter(field__isnull=True).first()

        self.assertIsNotNone(model)
        self.assertEqual(model.pk, created_pk)

    def test_binary_field(self):
        self.create_and_assert(models.BinaryFieldModel)

    def test_big_integer_field(self):
        self.create_and_assert(models.SearchableBigIntegerFieldModel)

    def test_boolean_field(self):
        self.create_and_assert(models.SearchableBooleanFieldModel)

    def test_char_field(self):
        self.create_and_assert(models.SearchableCharFieldModel)

    def test_date_field(self):
        self.create_and_assert(models.SearchableDateFieldModel)

    def test_datetime_field(self):
        self.create_and_assert(models.SearchableDateTimeFieldModel)

    def test_decimal_field(self):
        self.create_and_assert(models.SearchableDecimalFieldModel)

    def test_integer_field(self):
        self.create_and_assert(models.SearchableIntegerFieldModel)

    def test_json_field(self):
        self.create_and_assert(models.SearchableJSONFieldModel)

    def test_text_field(self):
        self.create_and_assert(models.SearchableTextFieldModel)

    def test_uuid_field(self):
        self.create_and_assert(models.SearchableUUIDFieldModel)


class UnsupportedLookupTestCase(test.TestCase):

    def test_char_field_contains(self):
        self.assertRaises(
            exceptions.LookupNotSupported,
            models.SearchableCharFieldModel.objects.filter,
            field__contains='test',
        )

    def test_non_searchable_char_field_exact(self):
        self.assertRaises(
            exceptions.LookupNotSupported,
            models.CharFieldModel.objects.filter,
            field='test',
        )

    def test_non_searchable_char_field_in(self):
        self.assertRaises(
            exceptions.LookupNotSupported,
            models.CharFieldModel.objects.filter,
            field__in=['test'],
        )


@test.override_settings(SECURED_FIELDS_HASH_SALT='test')
class EncryptedLookupBehaviorTestCase(test.TestCase):

    def setUp(self):
        self.first = models.SearchableCharFieldModel.objects.create(field='first')
        self.second = models.SearchableCharFieldModel.objects.create(field='second')
        self.null = models.SearchableCharFieldModel.objects.create(field=None)

    def assert_pks(self, queryset, expected):
        self.assertEqual(set(queryset.values_list('pk', flat=True)), {model.pk for model in expected})

    def test_exact_no_match(self):
        self.assertFalse(models.SearchableCharFieldModel.objects.filter(field='third').exists())

    def test_exact_is_case_sensitive(self):
        self.assertFalse(models.SearchableCharFieldModel.objects.filter(field='FIRST').exists())

    def test_exact_does_not_match_partial_value(self):
        self.assertFalse(models.SearchableCharFieldModel.objects.filter(field='firs').exists())

    def test_explicit_exact(self):
        self.assert_pks(models.SearchableCharFieldModel.objects.filter(field__exact='first'), [self.first])

    def test_exact_none(self):
        self.assert_pks(models.SearchableCharFieldModel.objects.filter(field=None), [self.null])

    def test_exact_with_another_salt(self):
        with self.settings(SECURED_FIELDS_HASH_SALT='another'):
            self.assertFalse(models.SearchableCharFieldModel.objects.filter(field='first').exists())

    def test_exclude(self):
        # NOTE: like for any nullable column, `exclude()` keeps the null rows
        self.assert_pks(models.SearchableCharFieldModel.objects.exclude(field='first'), [self.second, self.null])

    def test_get(self):
        self.assertEqual(models.SearchableCharFieldModel.objects.get(field='second').pk, self.second.pk)

    def test_or_condition(self):
        queryset = models.SearchableCharFieldModel.objects.filter(Q(field='first') | Q(field='second'))

        self.assert_pks(queryset, [self.first, self.second])

    def test_and_condition(self):
        queryset = models.SearchableCharFieldModel.objects.filter(Q(field='first') & Q(field='second'))

        self.assertFalse(queryset.exists())

    def test_in_multiple_matches(self):
        queryset = models.SearchableCharFieldModel.objects.filter(field__in=['first', 'second', 'third'])

        self.assert_pks(queryset, [self.first, self.second])

    def test_in_single_value(self):
        self.assert_pks(models.SearchableCharFieldModel.objects.filter(field__in=['second']), [self.second])

    def test_in_no_match(self):
        self.assertFalse(models.SearchableCharFieldModel.objects.filter(field__in=['third', 'fourth']).exists())

    def test_in_duplicated_values(self):
        self.assert_pks(models.SearchableCharFieldModel.objects.filter(field__in=['first', 'first']), [self.first])

    def test_in_empty(self):
        self.assertFalse(models.SearchableCharFieldModel.objects.filter(field__in=[]).exists())

    def test_in_with_none(self):
        """`None` is never matched by `in`, the same as on a regular field"""
        self.assert_pks(models.SearchableCharFieldModel.objects.filter(field__in=['first', None]), [self.first])

    def test_in_combined_with_other_filter(self):
        queryset = models.SearchableCharFieldModel.objects.filter(field__in=['first', 'second']).exclude(
            pk=self.first.pk
        )

        self.assert_pks(queryset, [self.second])

    def test_exclude_in(self):
        queryset = models.SearchableCharFieldModel.objects.exclude(field__in=['first', 'second'])

        self.assert_pks(queryset, [self.null])

    def test_isnull_false(self):
        self.assert_pks(models.SearchableCharFieldModel.objects.filter(field__isnull=False), [self.first, self.second])

    def test_isnull_on_non_searchable_field(self):
        model = models.CharFieldModel.objects.create(field=None)
        models.CharFieldModel.objects.create(field='test')

        self.assert_pks(models.CharFieldModel.objects.filter(field__isnull=True), [model])

    def test_get_or_create(self):
        model, created = models.SearchableCharFieldModel.objects.get_or_create(field='first')
        self.assertFalse(created)
        self.assertEqual(model.pk, self.first.pk)

        model, created = models.SearchableCharFieldModel.objects.get_or_create(field='third')
        self.assertTrue(created)
        self.assertEqual(models.SearchableCharFieldModel.objects.get(field='third').pk, model.pk)

    def test_boolean_false(self):
        true = models.SearchableBooleanFieldModel.objects.create(field=True)
        false = models.SearchableBooleanFieldModel.objects.create(field=False)

        self.assert_pks(models.SearchableBooleanFieldModel.objects.filter(field=False), [false])
        self.assert_pks(models.SearchableBooleanFieldModel.objects.filter(field=True), [true])

    def test_integer_zero_and_negative(self):
        zero = models.SearchableIntegerFieldModel.objects.create(field=0)
        negative = models.SearchableIntegerFieldModel.objects.create(field=-1)

        self.assert_pks(models.SearchableIntegerFieldModel.objects.filter(field=0), [zero])
        self.assert_pks(models.SearchableIntegerFieldModel.objects.filter(field__in=[-1, 1]), [negative])

    def test_integer_given_as_string(self):
        """The lookup value is prepared like the saved value, so `'100'` matches `100`"""
        model = models.SearchableIntegerFieldModel.objects.create(field=100)

        self.assert_pks(models.SearchableIntegerFieldModel.objects.filter(field='100'), [model])

    def test_empty_string(self):
        model = models.SearchableCharFieldModel.objects.create(field='')

        self.assert_pks(models.SearchableCharFieldModel.objects.filter(field=''), [model])

    def test_unicode(self):
        model = models.SearchableCharFieldModel.objects.create(field='สวัสดี 👋')

        self.assert_pks(models.SearchableCharFieldModel.objects.filter(field='สวัสดี 👋'), [model])
        self.assert_pks(models.SearchableCharFieldModel.objects.filter(field__in=['สวัสดี 👋']), [model])

    def test_value_containing_separator(self):
        model = models.SearchableCharFieldModel.objects.create(field='a$b')

        self.assertEqual(models.SearchableCharFieldModel.objects.get(pk=model.pk).field, 'a$b')
        self.assert_pks(models.SearchableCharFieldModel.objects.filter(field='a$b'), [model])

    def test_json_field_does_not_match_another_value(self):
        model = models.SearchableJSONFieldModel.objects.create(field={'name': 'John Doe'})

        self.assert_pks(models.SearchableJSONFieldModel.objects.filter(field={'name': 'John Doe'}), [model])
        self.assertFalse(models.SearchableJSONFieldModel.objects.filter(field={'name': 'Jane Doe'}).exists())

    def test_json_field_key_order_matters(self):
        """The hash is computed from the JSON text, so a different key order is a different value"""
        models.SearchableJSONFieldModel.objects.create(field={'a': 1, 'b': 2})

        self.assertFalse(models.SearchableJSONFieldModel.objects.filter(field={'b': 2, 'a': 1}).exists())

    def test_json_field_list(self):
        model = models.SearchableJSONFieldModel.objects.create(field=[1, 'two', None])

        self.assert_pks(models.SearchableJSONFieldModel.objects.filter(field=[1, 'two', None]), [model])

    def test_json_exact_lookup_is_registered(self):
        self.assertTrue(issubclass(lookups.EncryptedJSONExact, lookups.EncryptedExact))
        self.assertIs(
            models.SearchableJSONFieldModel._meta.get_field('field').get_lookup('exact'),  # pylint: disable=protected-access
            lookups.EncryptedJSONExact,
        )


class UnsupportedLookupForEveryFieldTestCase(test.TestCase):

    model_classes = [
        models.SearchableBigIntegerFieldModel,
        models.SearchableBooleanFieldModel,
        models.SearchableCharFieldModel,
        models.SearchableDateFieldModel,
        models.SearchableDateTimeFieldModel,
        models.SearchableDecimalFieldModel,
        models.SearchableIntegerFieldModel,
        models.SearchableJSONFieldModel,
        models.SearchableTextFieldModel,
        models.SearchableUUIDFieldModel,
    ]

    non_searchable_model_classes = [
        models.BigIntegerFieldModel,
        models.BooleanFieldModel,
        models.CharFieldModel,
        models.DateFieldModel,
        models.DateTimeFieldModel,
        models.DecimalFieldModel,
        models.IntegerFieldModel,
        models.JSONFieldModel,
        models.TextFieldModel,
        models.UUIDFieldModel,
    ]

    def test_unsupported_lookups(self):
        for model_class in self.model_classes:
            for lookup_name in ('gt', 'gte', 'lt', 'lte', 'iexact', 'contains', 'icontains', 'startswith',
                                'endswith', 'range', 'regex'):
                with self.subTest(model_class=model_class, lookup_name=lookup_name):
                    self.assertRaises(
                        exceptions.LookupNotSupported,
                        model_class.objects.filter,
                        **{f'field__{lookup_name}': 'value'},
                    )

    def test_non_searchable_exact_and_in(self):
        for model_class in self.non_searchable_model_classes:
            for lookup_name in ('exact', 'in'):
                with self.subTest(model_class=model_class, lookup_name=lookup_name):
                    self.assertRaises(
                        exceptions.LookupNotSupported,
                        model_class.objects.filter,
                        **{f'field__{lookup_name}': ['value'] if lookup_name == 'in' else 'value'},
                    )

    def test_non_searchable_isnull(self):
        for model_class in self.non_searchable_model_classes:
            with self.subTest(model_class=model_class):
                model = model_class.objects.create(field=None)

                self.assertEqual(model_class.objects.get(field__isnull=True).pk, model.pk)

    def test_binary_field_lookups(self):
        for lookup_name in ('exact', 'in', 'contains', 'startswith'):
            with self.subTest(lookup_name=lookup_name):
                self.assertRaises(
                    exceptions.LookupNotSupported,
                    models.BinaryFieldModel.objects.filter,
                    **{f'field__{lookup_name}': b'value'},
                )
