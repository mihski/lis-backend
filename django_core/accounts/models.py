from django.contrib.auth.models import (
    AbstractBaseUser, 
    BaseUserManager,
    PermissionsMixin
)
from django.db import models


class UserRole(models.Model):
    name = models.CharField(max_length=31, unique=True)


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=username,
            email=self.normalize_email(email)
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            username,
            email,
            password=password,
        )

        user.is_superuser = True
        user.save(using=self._db)
        
        return user


class User(AbstractBaseUser, PermissionsMixin):
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True)
    
    username = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100, default="", blank=True)
    last_name = models.CharField(max_length=100, default="", blank=True)
    middle_name = models.CharField(max_length=100, default="", blank=True)

    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    @property
    def is_staff(self):
        return self.is_superuser


class Profile(models.Model):
    GENDER = (
        ('male', 'Мужской'),
        ('female', 'Женский'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    first_name = models.CharField(max_length=63, blank=True)
    last_name = models.CharField(max_length=63, blank=True)
    middle_name = models.CharField(max_length=63, blank=True)

    gender = models.CharField(max_length=6, choices=GENDER, blank=True)

    scientific_director = models.ForeignKey('lessons.NPC', on_delete=models.SET_NULL, null=True, blank=True)

    head_form = models.CharField(max_length=15, blank=True)
    face_form = models.CharField(max_length=15, blank=True)
    hair_form = models.CharField(max_length=15, blank=True)
    dress_form = models.CharField(max_length=15, blank=True)


class ScientificDirector(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
