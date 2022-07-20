from django.contrib.auth.models import (
    AbstractBaseUser, 
    BaseUserManager,
    PermissionsMixin
)
from django.db import models


class UserRole(models.Model):
    name = models.CharField(max_length=31, unique=True)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
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
    REQUIRED_FIELDS = []

    @property
    def is_staff(self):
        return self.is_superuser


class Profile(models.Model):
    GENDER = (
        ('male', 'Мужской'),
        ('female', 'Женский'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)
    middle_name = models.CharField(max_length=63)

    gender = models.CharField(max_length=6, choices=GENDER)


class ScientificDirector(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
