from rest_framework.exceptions import APIException
from rest_framework import status


class NegativeResourcesException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "negative_resources"
    default_detail = "Resources is not supposed to be negative"


class EnergyOverfillException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "energy_overfill"
    default_detail = "Energy is not supposed to be overfilled"


class UltimateAlreadyActivatedException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "ultimate_already_activated"
    default_detail = "Ultimate has already activated"


class NotEnoughMoneyException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "not_enough_money"
    default_detail = "Your profile does not have enough money to perform action"


class NotEnoughEnergyException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "not_enough_energy"
    default_detail = "Your profile does not have enough energy to open this lesson"
