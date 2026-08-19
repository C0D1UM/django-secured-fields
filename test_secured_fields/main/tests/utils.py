import shutil
import uuid
from zoneinfo import ZoneInfo

from django.conf import settings


TZ_UTC = ZoneInfo('UTC')
TZ_BANGKOK = ZoneInfo('Asia/Bangkok')

UUID_1 = uuid.UUID('e8b5cd06-8b3f-4bbd-9a3b-2b2c8d64f8ea')
UUID_2 = uuid.UUID('9b0d1a4c-6f2e-4f8a-9d1b-77c0e5a3b210')


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
