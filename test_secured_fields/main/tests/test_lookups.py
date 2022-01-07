from django import test

from main import models


class EncryptedExactTestCase(test.TestCase):

    def test_charfield(self):
        models.SearchableCharFieldModel.objects.create(field='test')
        model = models.SearchableCharFieldModel.objects.filter(field='test').first()
        import ipdb; ipdb.set_trace()

        self.assertIsNotNone(model)
