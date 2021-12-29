from django import test


class SimpleTestCase(test.TestCase):
    """Simple tests"""

    def test_simple(self):
        self.assertTrue(True)
