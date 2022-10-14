from rest_framework.exceptions import ValidationError
from rest_framework import status


class NegativeResourcesException(ValidationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "Resources must be positive"
