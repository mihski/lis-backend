from rest_framework import serializers, validators
from accounts.models import User, Profile
from lessons.models import NPC


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'first_name', 'last_name', 'middle_name']
        read_only_fields = ['id', 'username', 'email', 'phone']


class ProfileSerializer(serializers.ModelSerializer):
    scientific_director = serializers.PrimaryKeyRelatedField(queryset=NPC.objects.all())

    def validate_scientific_director(self, scientific_director: NPC) -> NPC:
        if not scientific_director.is_scientific_director:
            raise validators.ValidationError("Is invalid NPC. Should be scientific director")

        return scientific_director

    class Meta:
        model = Profile
        fields = [
            'id',
            'first_name',
            'last_name',
            'middle_name',
            'gender',
            'scientific_director',
            'head_form',
            'face_form',
            'hair_form',
            'dress_form'
        ]
