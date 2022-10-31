from rest_framework.exceptions import APIException
from rest_framework import status


class NegativeResourcesException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "negative_resources"


class EnergyOverfillException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "energy_overfill"


class UltimateAlreadyActivatedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "ultimate_already_activated"


class NotEnoughMoneyException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "not_enough_money"


class NotEnoughEnergyException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "not_enough_energy"
