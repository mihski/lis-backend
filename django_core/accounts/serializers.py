from rest_framework.serializers import ModelSerializer
from accounts.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'first_name', 'last_name', 'middle_name']
        read_only_fields = ['id', 'username', 'email', 'phone']
