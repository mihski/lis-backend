from rest_framework.exceptions import ValidationError, NotFound
from rest_framework import status


class NegativeResourcesException(ValidationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "Resources must be positive"


class ResourcesOverfillException(ValidationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "Resource should not be overfilled"


class ResourcesNotFoundException(NotFound):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resources not found"
