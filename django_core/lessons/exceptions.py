from rest_framework.exceptions import APIException
from rest_framework import status


class BranchingAlreadyChosenException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "branching_already_chosen"


class NPCIsNotScientificDirectorException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "npc_not_scientific_director"


class UnitNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "unit_not_found"


class BlockNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "block_not_found"


class NotEnoughBlocksToSelectBranchException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "not_enough_blocks_for_branch"
