from rest_framework.viewsets import GenericViewSet
from rest_framework import response, decorators

from lessons.models import Unit


class CheckUnitSolution(GenericViewSet):
    queryset = Unit.objects.all()

    @decorators.action(methods=["POST"], detail=True, url_path='checkAnswer')
    def check_answer(self, request, *args, **kwargs):
        pass
