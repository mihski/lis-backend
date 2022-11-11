from django.urls import path
from sso_app.views import RedirectISU, GetISUToken, RedirectISUTest, GetISUTokenTest, LogoutISU

app_name = 'sso_app'

urlpatterns = [
    path('', RedirectISU.as_view(), name='redirect_isu'),
    path('logout/', LogoutISU.as_view(), name='logout_isu'),
    path('create/', GetISUToken.as_view(), name='get_isu_token'),
    path('test/', RedirectISUTest.as_view(), name='test_redirect_isu'),
    path('test/create/', GetISUTokenTest.as_view(), name='test_get_isu_token'),
]