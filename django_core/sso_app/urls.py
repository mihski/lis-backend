from django.urls import path
from sso_app.views import RedirectISU, GetISUToken

app_name = 'sso_app'

urlpatterns = [
    path('', RedirectISU.as_view(), name='redirect_isu'),
    path('redirect/', GetISUToken.as_view(), name='get_isu_token')
]