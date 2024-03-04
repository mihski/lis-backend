from rest_framework.exceptions import APIException
from rest_framework import status


class AssignmentNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "assignment_not_found"
    default_detail = "Assignment not found"
