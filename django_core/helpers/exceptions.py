from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import APIException


def custom_exception_handler(exception: Exception, context: dict) -> Response:
    response: Response = exception_handler(exception, context)
    if response is not None and isinstance(exception, APIException):
        response.data["error_code"] = exception.get_codes()

    return response
