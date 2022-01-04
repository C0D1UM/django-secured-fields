import shutil

from django.conf import settings


class NoValue:
    pass


class FileTestMixin(object):
    """
    Delete created files after ran test
    Ref: https://dirtycoder.net/2016/02/09/testing-a-model-that-have-an-imagefield/
    """

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
