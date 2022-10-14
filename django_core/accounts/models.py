from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserRole(models.Model):
    """
        Таблица БД для хранения ролей пользователей
    """
    name = models.CharField(max_length=31, unique=True)

    class Meta:
        app_label = "accounts"
        verbose_name = "UserRole"
        verbose_name_plural = "UserRoles"


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None) -> AbstractBaseUser:
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            username=username,
            email=self.normalize_email(email)
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password=None) -> AbstractBaseUser:
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

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    @property
    def is_staff(self):
        return self.is_superuser

    class Meta:
        app_label = "accounts"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __repr__(self) -> str:
        return f"{self.username}"

    def __str__(self) -> str:
        return repr(self)


class UniversityPosition(models.TextChoices):
    """
        Роль персонажа в университете
    """
    STUDENT = "Студент"
    INTERN = "Стажер"
    LABORATORY_ASSISTANT = "Лаборант"
    ENGINEER = "Инженер"
    JUN_RESEARCH_ASSISTANT = "Мл. научный сотрудник"


class Profile(models.Model):
    """
        Таблица БД для хранения профилей персонажей
    """
    GENDER = (
        ("male", "Мужской"),
        ("female", "Женский"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)
    middle_name = models.CharField(max_length=63)
    gender = models.CharField(max_length=6, choices=GENDER)  # todo: по-хорошему тоже на TextChoices заменить
    university_position = models.CharField(
        choices=UniversityPosition.choices,
        default=UniversityPosition.STUDENT,
        max_length=40
    )

    class Meta:
        app_label = "accounts"
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name} - {self.user.username}"

    def __str__(self) -> str:
        return repr(self)


class ScientificDirector(models.Model):
    """
        Таблица БД для хранения научных руководителей
    """
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        app_label = "accounts"
        verbose_name = "ScientificDirector"
        verbose_name_plural = "ScientificDirectors"

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name} - {self.name}"

    def __str__(self) -> str:
        return repr(self)
