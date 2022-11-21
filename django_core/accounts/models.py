from django.conf import settings
from django.db import models
from django.apps import apps
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django_lifecycle import (
    LifecycleModel,
    hook,
    AFTER_CREATE,
    AFTER_UPDATE,
    BEFORE_UPDATE
)

from accounts.choices import UniversityPosition, PROFILE_GENDER, LABORATORIES
from resources.models import Resources
from resources.utils import get_max_energy_by_position


class UserRole(models.Model):
    """
        Таблица БД для хранения ролей пользователей
    """
    name = models.CharField(max_length=31, unique=True)

    class Meta:
        app_label = "accounts"
        verbose_name = "UserRole"
        verbose_name_plural = "UserRoles"

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name} - {self.name}"

    def __str__(self) -> str:
        return repr(self)


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


class User(AbstractBaseUser, PermissionsMixin, LifecycleModel):
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

    @hook(AFTER_CREATE)
    def create_related_profile(self) -> None:
        from accounts.tasks import generate_profile_images

        profile = Profile.objects.create(
            user=self,
            isu=self.username,
            username=None,
            gender=None,
            head_form=ProfileAvatarHead.objects.first(),
            face_form=ProfileAvatarFace.objects.first(),
            hair_form=ProfileAvatarHair.objects.first(),
            cloth_form=ProfileAvatarClothes.objects.first(),
            brows_form=ProfileAvatarBrows.objects.first(),
        )
        generate_profile_images(profile.id)

    class Meta:
        app_label = "accounts"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name} - {self.username}"

    def __str__(self) -> str:
        return repr(self)


class ProfileAvatarBodyPart(models.Model):
    gender = models.CharField(max_length=6, choices=PROFILE_GENDER)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__}[{self.id}] {self.gender}"


class ProfileAvatarHead(ProfileAvatarBodyPart):
    usual_part = models.ImageField(
        upload_to='body_part/heads/',
        default='woman_parts/Head/1 type/Woman-1-head@4x.png'
    )

    class Meta:
        app_label = "accounts"
        verbose_name = "ProfileAvatarHead"
        verbose_name_plural = "ProfileAvatarHeads"

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name}[{self.id}]"

    def __str__(self) -> str:
        return repr(self)


class ProfileAvatarHair(ProfileAvatarBodyPart):
    color = models.CharField(max_length=3, default=0)

    front_part = models.ImageField(
        upload_to='body_part/hairs/',
        default='woman_parts/Hair/1 type/Woman-1-hair-front-red@4x.png'
    )
    back_part = models.ImageField(
        upload_to='body_part/hairs/',
        default='woman_parts/Hair/1 type/Woman-1-hair-back-red@4x.png',
        null=True,
        blank=True
    )

    class Meta:
        app_label = "accounts"
        verbose_name = "ProfileAvatarHair"
        verbose_name_plural = "ProfileAvatarHair"

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name}[{self.id}]"

    def __str__(self) -> str:
        return repr(self)


class ProfileAvatarFace(ProfileAvatarBodyPart):
    usual_part = models.ImageField(
        upload_to='body_part/faces/',
        default='woman_parts/Face/1 type/Woman-1-face-usual@4x.png',
    )
    fair_part = models.ImageField(
        upload_to='body_part/faces/',
        default='woman_parts/Face/1 type/Woman-1-face-fair@4x.png',
    )
    happy_part = models.ImageField(
        upload_to='body_part/faces/',
        default='woman_parts/Face/1 type/Woman-1-face-happy@4x.png',
    )
    angry_part = models.ImageField(
        upload_to='body_part/faces/',
        default='woman_parts/Face/1 type/Woman-1-face-angry@4x.png',
    )

    class Meta:
        app_label = "accounts"
        verbose_name = "ProfileAvatarFace"
        verbose_name_plural = "ProfileAvatarFaces"

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name}[{self.id}]"

    def __str__(self) -> str:
        return repr(self)


class ProfileAvatarBrows(ProfileAvatarBodyPart):
    face = models.ManyToManyField(
        ProfileAvatarFace,
        blank=True,
        default=None,
        related_name="brows_list"
    )
    # TODO: make generic
    type = models.CharField(max_length=20)
    color = models.CharField(max_length=3, default=0)

    usual_part = models.ImageField(
        upload_to='body_part/brows/',
        default='woman_parts/Brows/1 type/Woman-1-brows-usual-light@4x.png',
    )
    fair_part = models.ImageField(
        upload_to='body_part/brows/',
        default='woman_parts/Brows/1 type/Woman-1-brows-fair-light@4x.png',
    )
    happy_part = models.ImageField(
        upload_to='body_part/brows/',
        default='woman_parts/Brows/1 type/Woman-1-brows-happy-light@4x.png',
    )
    angry_part = models.ImageField(
        upload_to='body_part/brows/',
        default='woman_parts/Brows/1 type/Woman-1-brows-angry-light@4x.png',
    )

    class Meta:
        app_label = "accounts"
        verbose_name = "ProfileAvatarBrows"
        verbose_name_plural = "ProfileAvatarBrows"

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name}[{self.id}]"

    def __str__(self) -> str:
        return repr(self)


class ProfileAvatarClothes(ProfileAvatarBodyPart):
    usual_part = models.ImageField(
        upload_to='body_part/clothes/',
        default='woman_parts/Brows/1 type/Woman-1-clothes-usual@4x.png',
    )
    fair_part = models.ImageField(
        upload_to='body_part/clothes/',
        default='woman_parts/Brows/1 type/Woman-1-clothes-fair@4x.png',
    )
    happy_part = models.ImageField(
        upload_to='body_part/clothes/',
        default='woman_parts/Brows/1 type/Woman-1-clothes-happy@4x.png',
    )
    angry_part = models.ImageField(
        upload_to='body_part/clothes/',
        default='woman_parts/Brows/1 type/Woman-1-clothes-angry@4x.png',
    )

    class Meta:
        app_label = "accounts"
        verbose_name = "ProfileAvatarClothes"
        verbose_name_plural = "ProfileAvatarClothes"

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name}[{self.id}]"

    def __str__(self) -> str:
        return repr(self)


def _upload_avatar_image(instance: "Profile", filename: str) -> str:
    return "/".join(["avatars", instance.user.username, filename])


class Profile(LifecycleModel):
    """
        Таблица БД для хранения профилей персонажей
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile", null=True)
    username = models.CharField(max_length=63, null=True, blank=True)
    isu = models.CharField(max_length=31, default="", editable=False)
    gender = models.CharField(max_length=6, choices=PROFILE_GENDER, null=True)
    university_position = models.CharField(
        choices=UniversityPosition.choices,
        default=UniversityPosition.STUDENT,
        max_length=40
    )
    course = models.ForeignKey(
        "lessons.Course",
        on_delete=models.CASCADE,
        related_name="profiles",
        default=1
    )
    scientific_director = models.ForeignKey("lessons.NPC", on_delete=models.SET_NULL, null=True, blank=True)
    laboratory = models.CharField(max_length=120, choices=LABORATORIES, default="it")

    head_form = models.ForeignKey("ProfileAvatarHead", on_delete=models.CASCADE, null=True, blank=True)
    face_form = models.ForeignKey("ProfileAvatarFace", on_delete=models.CASCADE, null=True, blank=True)
    hair_form = models.ForeignKey("ProfileAvatarHair", on_delete=models.CASCADE, null=True, blank=True)
    brows_form = models.ForeignKey("ProfileAvatarBrows", on_delete=models.CASCADE, null=True, blank=True)
    cloth_form = models.ForeignKey("ProfileAvatarClothes", on_delete=models.CASCADE, null=True, blank=True)

    usual_image = models.ImageField(upload_to=_upload_avatar_image, null=True, editable=False)
    angry_image = models.ImageField(upload_to=_upload_avatar_image, null=True, editable=False)
    fair_image = models.ImageField(upload_to=_upload_avatar_image, null=True, editable=False)
    happy_image = models.ImageField(upload_to=_upload_avatar_image, null=True, editable=False)

    ultimate_activated = models.BooleanField(default=0)
    ultimate_finish_datetime = models.DateTimeField(null=True, default=None, blank=True)

    @hook(AFTER_CREATE)
    def create_related_entities(self) -> None:
        Resources.objects.create(user=self, money_amount=10000)
        Statistics.objects.create(profile=self)

    @hook(AFTER_UPDATE, when="university_position", has_changed=True)
    def update_energy_on_university_position_change(self):
        max_energy = get_max_energy_by_position(self.university_position)
        self.resources.set_energy(max_energy)
        self.resources.save()

    @hook(BEFORE_UPDATE, when="scientific_director", has_changed=True, is_now=None)
    def set_scientific_director_by_default(self) -> None:
        npc_model = apps.get_model("lessons.NPC")
        npc_uid: str = settings.DEFAULT_SCIENTIFIC_DIRECTOR_UID

        self.scientific_director = npc_model.objects.filter(uid=npc_uid).first()
        self.scientific_director.save()

    @hook(BEFORE_UPDATE, when="scientific_director", has_changed=True, was_not=None, is_not=None)
    def decrease_energy_on_scientific_director_change(self) -> None:
        from resources.utils import check_ultimate_is_active

        if check_ultimate_is_active(self):
            return

        self.resources.energy_amount -= settings.CHANGE_SCIENTIFIC_DIRECTOR_ENERGY_COST
        self.resources.save()

    class Meta:
        app_label = "accounts"
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name} - {self.username}"

    def __str__(self):
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


class Statistics(models.Model):
    """
        Таблица БД для хранения статистики профиля
    """
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="statistics")
    quests_done = models.IntegerField(default=0)
    lessons_done = models.IntegerField(default=0)
    total_time_spend = models.IntegerField(default=0)

    class Meta:
        app_label = "accounts"
        verbose_name = "ProfileStatistics"
        verbose_name_plural = "ProfilesStatistics"

    def __repr__(self) -> str:
        return f"{self._meta.verbose_name} - {self.profile.username}"

    def __str__(self):
        return repr(self)
