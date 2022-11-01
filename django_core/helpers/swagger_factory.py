import json
from collections import defaultdict
from typing import Type, Optional

from rest_framework.exceptions import APIException


class SwaggerFactory:
    """
        Класс, генерирующий параметры для декоратора
        swagger_auto_schema из drf_yasg
    """

    def __new__(cls):
        """
            Реализация синглтона (экономим память)
        """
        if not hasattr(cls, "instance"):
            cls.instance = super(SwaggerFactory, cls).__new__(cls)
        return cls.instance

    def _get_responses(self, responses: Optional[list[Type[APIException]]]) -> dict:
        if responses is None: return {}
        output: dict[int, str] = defaultdict()

        for exception in responses:
            status = exception.status_code
            data = json.dumps({
                "error_code": exception.default_code,
                "detail": exception.default_detail
            })
            if status in output:
                output[status] += f"\n{data}"
            else:
                output[status] = data

        return {"responses": output}

    def _get_methods(self, methods: Optional[list[str]]) -> dict:
        if methods is None: return {}
        return {"methods": methods}

    def __call__(
            self,
            *,
            methods: Optional[list[str]] = None,
            responses: Optional[list[Type[APIException]]] = None
    ) -> dict:
        """
            Вызываем класс как функцию -> получаем аргументы.
            Можно модернизировать, добавив доп поля
        """
        total_params = {}
        total_params.update(self._get_methods(methods))
        total_params.update(self._get_responses(responses))
        return total_params
