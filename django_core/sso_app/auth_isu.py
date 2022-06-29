import requests
from django.conf import settings
import jwt
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

class ISUManager():

  def __init__(self):

    for param_name, param_value \
        in settings.ISU_MANAGER_CONFIG.items():
            setattr(self, param_name, param_value)
    
    self.auth_url = f"{self.base_uri}auth?"
    self.obtain_token_url = f"{self.base_uri}token?"
  
  def obtain_auth_url(self):

    auth_url = ''.join(
        [
            self.auth_url,
            f"response_type={self.response_type}&",
            f"scope={self.scope}&",
            f"client_id={self.client_id}&",
            f"redirect_uri={self.redirect_uri}"
        ]
    )
    
    return auth_url
  
  def authorize(self, code):

    payload = '&'.join(
        [
            f"client_id={self.client_id}",
            f"client_secret={self.client_secret}",
            f"grant_type={self.grant_type}",
            f"redirect_uri={self.redirect_uri}",
            f"code={code}"
        ]
    )
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.request(
        "POST",
        self.obtain_token_url,
        headers=headers,
        data=payload
    )

    return self.get_or_create_user(response.json()['id_token'])

# TODO: вернуть, когда появится модель профиля
#   @staticmethod
#   def create_profile(user, middle_name=None):
#     profile = Profile.objects.create(
#       user=user,
#       first_name=user.first_name,
#       last_name=user.last_name,
#       middle_name=middle_name,
#     )
  
  def get_or_create_user(self, id_token):

    user_data = jwt.decode(id_token, verify=False)
    username = user_data.get('isu')
    user_instance = User.objects.filter(username=username)

    if not user_instance.exists():
        email = user_data.get("corp_email") \
            if user_data.get("corp_email") \
            else user_data.get("email")

        first_name, last_name, middle_name = \
            user_data.get('given_name'), \
            user_data.get('family_name'), \
            user_data.get('middle_name')

        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )

        user.set_unusable_password()

        self.create_profile(user, middle_name)

    else:
        user = user_instance.first()

    refresh = RefreshToken.for_user(user)

    return str(refresh), str(refresh.access_token)
