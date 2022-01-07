import shutil

from django.conf import settings


class NoValue:
    pass


class FileTestMixin:
    """
    Delete created files after ran test
    Ref: https://dirtycoder.net/2016/02/09/testing-a-model-that-have-an-imagefield/
    """

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
