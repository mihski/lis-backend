import requests
import logging

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


logger = logging.Logger(__name__)


class ISUManager:
    def __init__(self):
        for param_name, param_value in settings.ISU_MANAGER_CONFIG.items():
            setattr(self, param_name, param_value)

        self.auth_url = f"{self.base_uri}auth?"
        self.obtain_token_url = f"{self.base_uri}token?"

    def obtain_auth_url(self):
        auth_url = ''.join([
            self.auth_url,
            f"response_type={self.response_type}&",
            f"scope={self.scope}&",
            f"client_id={self.client_id}&",
            f"redirect_uri={self.redirect_uri}"
        ])

        return auth_url

    def obtail_logout_url(self):
        return ''.join([
            self.logout_url,
            f"?client_id={self.client_id}&",
            f"post_logout_redirect_uri={self.post_logout_redirect_uri}"
        ])

    def authorize(self, code):
        payload = '&'.join([
            f"client_id={self.client_id}",
            f"client_secret={self.client_secret}",
            f"grant_type={self.grant_type}",
            f"redirect_uri={self.redirect_uri}",
            f"code={code}"
        ])

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.request(
            "POST",
            self.obtain_token_url,
            headers=headers,
            data=payload
        )
        result = response.json()
        jwt_token = result.get("id_token", "")

        if not jwt_token:
            logger.warning(f"There is no isu_token on response(code={response.status_code}) {result}")
            raise ValidationError("Something went wrong")

        return self.get_or_create_user(jwt_token)

    def create_user(self, user_data):
        username = user_data.get('isu', user_data.get('email'))

        email = user_data.get('corp_email', user_data.get('email'))

        first_name, last_name, middle_name = (
            user_data.get('given_name'),
            user_data.get('family_name'),
            user_data.get('middle_name')
        )

        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            is_active=True
        )

        user.set_unusable_password()

        return user

    def get_or_create_user(self, id_token):
        user_data = jwt.decode(id_token, options={"verify_signature": False})
        user = User.objects.filter(
            username=user_data.get('isu', user_data.get('email'))
        ).first()

        if not user:
            user = self.create_user(user_data)

        refresh_token = RefreshToken.for_user(user)

        return str(refresh_token), str(refresh_token.access_token)
