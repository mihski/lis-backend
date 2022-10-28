from rest_framework.exceptions import APIException
from rest_framework import status


class BranchingAlreadyChosenException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "branching_already_chosen"
