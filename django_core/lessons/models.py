from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db import models
from django_lifecycle import LifecycleModel, hook, AFTER_CREATE

from lessons.tasks import upload_profile_course_finished_gsheets

User = get_user_model()

GENDERS = (
    ("any", "Любой"),
    ("male", "Мужской"),
    ("female", "Женский"),
)


def default_locale():
    return {'ru': {}, 'en': {}}


class UnitAffect(models.Model):
    class UnitCodeType(models.TextChoices):
        LABORATORY_CHOICE = "laboratory_choice"
        JOB_CHOICE = "job_choice"
        SALARY = "salary"

    code = models.CharField(max_length=31, choices=UnitCodeType.choices)
    content = models.JSONField()

    def clean(self):
        if self.code == UnitAffect.UnitCodeType.SALARY:
            if not "amount" not in self.content:
                raise ValidationError("Salary content have to has amount")

            if not isinstance(self.content["amount"], int) and self.content["amount"] != "by_position":
                raise ValidationError("Salary should be int or 'by_position' string")

        return super().clean()

    def __str__(self):
        return f"UnitAffect[{self.id}] {self.code}"


class EditorBlockModel(models.Model):
    block_id = models.IntegerField(default=None, null=True, blank=True)  # deprecated
    local_id = models.CharField(max_length=255, default="", blank=True)  # n_1660813403095
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)

    class Meta:
        abstract = True


class Course(models.Model):
    """
        Таблица БД для хранения информации о курсах
    """
    name = models.CharField(max_length=127)
    description = models.TextField()

    entry = models.CharField(default=None, max_length=120, blank=True, null=True)
    locale = models.JSONField(default=default_locale)

    is_editable = models.BooleanField(default=True)

    start_money = models.IntegerField(default=500)
    start_energy = models.IntegerField(default=0)

    def __str__(self):
        return f"Course[{self.id}] {self.name}"


class Quest(EditorBlockModel):
    """
        Таблица БД для хранения информации о квестах
        Квест - цепочка уроков
    """
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL, related_name="quests")

    name = models.CharField(max_length=127)
    description = models.TextField()

    entry = models.CharField(default=None, max_length=120, blank=True, null=True)
    next = models.CharField(default=None, max_length=120, blank=True, null=True)

    def __str__(self):
        return self.name


class Branching(EditorBlockModel):
    """
        Таблица БД для хранения информации о ветвлениях
        Ветвление бывает: OneToMany и ManyToOne
    """
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL, related_name="branchings")
    quest = models.ForeignKey(Quest, default=None, null=True, blank=True, on_delete=models.SET_NULL,
                              related_name="branchings")
    type = models.IntegerField()
    content = models.JSONField()


class ProfileBranchingChoice(models.Model):
    """
        Таблица БД для хранения информации о выборе
        ветвления определенным профилем игрока
    """
    profile = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE)
    branching = models.ForeignKey("Branching", on_delete=models.CASCADE)
    choose_local_id = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"ProfileBranchingChoice[{self.id}] {self.profile} on {self.branching.local_id}"


class Laboratory(models.Model):
    """
        Таблица БД для хранения информации о лабораториях
    """
    name = models.CharField(max_length=127)


class LessonBlock(models.Model):
    """
        Таблица БД для хранения мета-информации уроков
    """
    locale = models.JSONField(default=default_locale)
    markup = models.JSONField(default=default_locale)
    entry = models.CharField(default=None, max_length=120, blank=True, null=True)  # if root -> local_id 1st unit


class Lesson(EditorBlockModel):
    """
        Таблица БД для хранения информации об уроках
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    quest = models.ForeignKey(Quest, null=True, on_delete=models.SET_NULL, related_name="lessons", blank=True)
    laboratory = models.ForeignKey(Laboratory, on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=127)
    description = models.TextField()
    for_gender = models.CharField(default="any", max_length=6, choices=GENDERS)

    time_cost = models.IntegerField()
    money_cost = models.IntegerField()
    energy_cost = models.IntegerField()

    has_bonuses = models.BooleanField(default=False)

    bonuses = models.JSONField(default=dict, blank=True)
    content = models.OneToOneField(LessonBlock, related_name="lesson", on_delete=models.CASCADE)

    next = models.CharField(max_length=255, default="", blank=True)

    profile_affect = models.ForeignKey("UnitAffect", null=True, on_delete=models.SET_NULL, blank=True)

    def __str__(self):
        return f"Lesson[{self.id}] {self.course}"


class Unit(EditorBlockModel):
    """
        Таблица БД для хранения информации о частях урока.
        Урок - последовательная цепочка юнитов.
    """
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True)
    lesson_block = models.ForeignKey(LessonBlock, on_delete=models.SET_NULL, null=True, related_name="blocks")
    type = models.IntegerField()
    content = models.JSONField()
    next = models.JSONField()
    profile_affect = models.ForeignKey("UnitAffect", null=True, on_delete=models.SET_NULL, blank=True)


class NPC(models.Model):
    """
        Таблица БД для хранения информации об NPC
    """

    class NPCGenders(models.TextChoices):
        MALE = "male"
        FEMALE = "female"

    uid = models.CharField(max_length=7, unique=True)

    ru_name = models.CharField(max_length=31)
    en_name = models.CharField(max_length=31)

    gender = models.CharField(max_length=6, choices=NPCGenders.choices, default=NPCGenders.MALE)
    age = models.IntegerField(default=0)

    ru_description = models.TextField(blank=True)
    en_description = models.TextField(blank=True)

    ru_tags = models.CharField(max_length=255, blank=True)
    en_tags = models.CharField(max_length=255, blank=True)

    is_scientific_director = models.BooleanField(default=False)

    usual_image = models.ImageField(upload_to="npc_emotions")
    angry_image = models.ImageField(upload_to="npc_emotions")
    fair_image = models.ImageField(upload_to="npc_emotions")
    sad_image = models.ImageField(upload_to="npc_emotions")

    def __str__(self):
        return f"NPC[{self.uid}] {self.ru_name}"


class Location(models.Model):
    """
        Таблица БД для хранения информации о локациях
    """
    uid = models.CharField(max_length=7, unique=True)
    ru_name = models.CharField(max_length=31)
    en_name = models.CharField(max_length=31)

    image = models.ImageField(upload_to="locations")
    image_disabled = models.ImageField(upload_to="locations")

    def __str__(self):
        return f"Location[{self.uid}] {self.ru_name}"


class CourseMapImg(models.Model):
    """
        Таблица БД для хранения карт курсов
    """
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    image = models.ImageField(upload_to="course_map_images")
    image_disabled = models.ImageField(upload_to="course_map_images")

    def __str__(self):
        return f"CourseMapImg[{self.order}] for {self.course.name}"


class EmailTypes(models.TextChoices):
    CONTENT = "content"
    TECH = "tech"


class Review(models.Model):
    """
        Таблица БД для хранения отзывов
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    mail_type = models.CharField(max_length=7, choices=EmailTypes.choices, default=EmailTypes.CONTENT)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "lessons"
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ("created_at",)


class Question(models.Model):
    """
        Таблица БД для хранения вопросов
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "lessons"
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ("created_at",)


class ProfileLessonDone(models.Model):
    profile = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE, related_name="lessons_done")
    lesson = models.ForeignKey("Lesson", on_delete=models.CASCADE)
    finished_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "lessons"
        verbose_name = "ProfileLessonDone"
        verbose_name_plural = "ProfileLessonsDone"
        ordering = ("finished_at",)

    def __repr__(self) -> str:
        return f"[{self.lesson.name}] {self.profile.username}"

    def __str__(self) -> str:
        return repr(self)


class ProfileCourseDone(LifecycleModel):
    profile = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    finished_at = models.DateTimeField(auto_now=True)

    @hook(AFTER_CREATE)
    def transfer_data_to_google_sheets(self):
        from lessons.serializers import ProfileCourseFinishedSerializer

        serialized_data = ProfileCourseFinishedSerializer(self).data
        upload_profile_course_finished_gsheets.delay(serialized_data)

    class Meta:
        app_label = "lessons"
        verbose_name = "ProfileCourseDone"
        verbose_name_plural = "ProfileCoursesDone"
        ordering = ("finished_at",)

    def __repr__(self) -> str:
        return f"[{self.course.name}] {self.profile.username}"

    def __str__(self) -> str:
        return repr(self)


class ProfileLesson(models.Model):
    player = models.ForeignKey("accounts.Profile", on_delete=models.CASCADE)
    location = models.IntegerField(default=1)
    npc = models.IntegerField(default=1)
    lesson_name = models.CharField(max_length=32, default="")
    lesson_number = models.IntegerField(default=0)
    quest_number = models.IntegerField(default=0)
    locales = models.JSONField(default=default_locale)


class ProfileLessonChunk(models.Model):
    lesson = models.ForeignKey(ProfileLesson, on_delete=models.CASCADE)
    type = models.IntegerField(default=0)
    content = models.JSONField(default={})
    local_id = models.CharField(max_length=64, default="", blank=True)
