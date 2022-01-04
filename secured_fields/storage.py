from django.core.files.storage import FileSystemStorage

from . import mixins


class EncryptedFileSystemStorage(mixins.EncryptedStorageMixin, FileSystemStorage):
    pass
