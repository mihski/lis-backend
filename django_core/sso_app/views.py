from rest_framework.generics import ListAPIView
from django.http import HttpResponseRedirect, HttpResponse
from sso_app.auth_isu import ISUManager

class RedirectISU(ListAPIView):
    """
    Вьюшка для редиректа на CAS авторизацию.
    В случае успешной авторазции возвращает
    нам на redirect_url код авторизации.
    """
    def get(self, request):
      
        isu_manager = ISUManager()
        return HttpResponseRedirect(isu_manager.obtain_auth_url())

class GetISUToken(ListAPIView):
    """
    Вьюшка для получения токенов пользователя
    по коду авторазции
    """
    def get(self, request):

        code = request.GET.get('code')
        isu_manager = ISUManager()
        refresh_token, access_token = isu_manager.authorize(code)
        return HttpResponseRedirect(f"https://list.itmo.ru/auth/isu/{refresh_token}/{access_token}/")
