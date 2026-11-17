from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateEnrollmentDocumentStorage(FileSystemStorage):
    def __init__(self) -> None:
        super().__init__(base_url=None)

    @property
    def location(self) -> str:
        return str(settings.PRIVATE_MEDIA_ROOT)
