from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from sso_app.auth_isu import ISUManager


class RedirectISU(APIView):
    """ Вьюшка для редиректа на CAS авторизацию.
    В случае успешной авторазции возвращает нам на redirect_url код авторизации.
    """
    def get(self, request):
        isu_manager = ISUManager()

        return HttpResponseRedirect(isu_manager.obtain_auth_url())


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
