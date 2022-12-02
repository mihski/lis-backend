import logging

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import APIException

logger = logging.Logger(__name__)


def custom_exception_handler(exception: APIException, context: dict) -> Response:
    response: Response = exception_handler(exception, context)

    if response:
        response.data.update(error_code=exception.get_codes())
        logger.warning(str(response.data))

    return response
