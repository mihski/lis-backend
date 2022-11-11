from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from sso_app.auth_isu import ISUManager

from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutISU(APIView):
    def get(self, request):
        isu_manager = ISUManager()

        return HttpResponseRedirect(isu_manager.obtail_logout_url())


class RedirectISU(APIView):
    """ Вьюшка для редиректа на CAS авторизацию.
    В случае успешной авторазции возвращает нам на redirect_url код авторизации.
    """
    def get(self, request):
        isu_manager = ISUManager()

        return HttpResponseRedirect(isu_manager.obtain_auth_url())


class RedirectISUTest(APIView):
    """ Вьюшка для теста редиректа на CAS авторизацию.
    Симулирует возвращение code.
    """
    def get(self, request):
        return HttpResponseRedirect('http://localhost:3000/auth/?code=ASDNKJE83jS')


class GetISUToken(APIView):
    """ Вьюшка для получения токенов пользователя по коду авторазции """
    def get(self, request):
        code = request.GET.get('code')
        isu_manager = ISUManager()
        refresh_token, access_token = isu_manager.authorize(code)
 
        return Response({
            'refresh_token': refresh_token,
            'access_token': access_token,
        })


class GetISUTokenTest(APIView):
    """ Вьюшка для получения токенов пользователя по коду авторазции
    Возвращает токены для тестового пользователя
    """

    def get(self, request):
        api_test_username = 'api_test'

        user = User.objects.filter(username=api_test_username).first()

        if not user:
            user = User.objects.create_user(
                username=api_test_username,
                email='api_test@mail.ru',
                password='password',
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        })
