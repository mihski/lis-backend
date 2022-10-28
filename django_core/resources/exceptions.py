from rest_framework.exceptions import ValidationError, NotFound, APIException
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


class UltimateAlreadyActivatedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "Ultimate already activated"


class NotEnoughMoneyException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "not_enough_money"


class NotEnoughEnergyException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "not_enough_energy"
