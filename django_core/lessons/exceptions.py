from rest_framework.exceptions import APIException
from rest_framework import status


class LessonForbiddenException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "lesson_forbidden_exception"
    default_detail = "Your lesson_key does not equal to the actual one"


class BranchingAlreadyChosenException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "branching_already_chosen"
    default_detail = "You have already selected this branching"


class NPCIsNotScientificDirectorException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "npc_not_scientific_director"
    default_detail = "NPC is not scientific director"


class FirstScientificDirectorIsNotDefaultException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "first_scientific_director_is_not_default"
    default_detail = "First scientific director should be default"


class UnitNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "unit_not_found"
    default_detail = "Unit not found"


class BlockNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "block_not_found"
    default_detail = "Block not found"


class NotEnoughBlocksToSelectBranchException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "not_enough_blocks_for_branch"
    default_detail = "Not enough blocks to select branch"


class BlockEntityIsUnavailableException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "block_entity_is_inaccessible"
    default_detail = "Finish previous lessons to get access"


class NotAllTasksDoneException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "not_all_tasks_done"
    default_detail = "Finish undone tasks"


class CanNotSkipLessonException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "can_not_skip_lesson"
    default_detail = "You can skip only once per course"
