from django.db import models


GENDERS = (
    ('any', 'Любой'),
    ('male', 'Мужской'),
    ('female', 'Женский'),
)


class EditorBlockModel(models.Model):
    block_id = models.IntegerField(default=None, null=True, blank=True)
    local_id = models.CharField(max_length=255, default='', blank=True)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)

    class Meta:
        abstract = True


class Course(models.Model):
    name = models.CharField(max_length=127)
    description = models.TextField()

    entry = models.CharField(default=None, max_length=120, blank=True, null=True)
    locale = models.JSONField(default=dict)

    is_editable = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Quest(EditorBlockModel):
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL, related_name='quests')

    name = models.CharField(max_length=127)
    description = models.TextField()

    entry = models.CharField(default=None, max_length=120, blank=True, null=True)
    next = models.CharField(default=None, max_length=120, blank=True, null=True)

    def __str__(self):
        return self.name


class Branching(EditorBlockModel):
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL, related_name='branchings')
    quest = models.ForeignKey(Quest, default=None, null=True, blank=True, on_delete=models.SET_NULL, related_name='branchings')
    type = models.IntegerField()
    content = models.JSONField()


class Laboratory(models.Model):
    name = models.CharField(max_length=127)


class LessonBlock(models.Model):
    locale = models.JSONField(default=dict)
    markup = models.JSONField(default={'ru': [], 'en': []})
    entry = models.CharField(default=None, max_length=120, blank=True, null=True)


class Lesson(EditorBlockModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    quest = models.ForeignKey(Quest, null=True, on_delete=models.SET_NULL, related_name='lessons')
    laboratory = models.ForeignKey(Laboratory, on_delete=models.SET_NULL, null=True)

    name = models.CharField(max_length=127)
    description = models.TextField()
    for_gender = models.CharField(default='any', max_length=6, choices=GENDERS)

    time_cost = models.IntegerField()
    money_cost = models.IntegerField()
    energy_cost = models.IntegerField()

    has_bonuses = models.BooleanField(default=False)

    bonuses = models.JSONField(default=dict)
    content = models.OneToOneField(LessonBlock, related_name='lesson', on_delete=models.CASCADE)

    next = models.CharField(max_length=255, default='', blank=True)

    def __str__(self):
        return self.name


class Unit(EditorBlockModel):
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True)
    lesson_block = models.ForeignKey(LessonBlock, on_delete=models.SET_NULL, null=True, related_name='blocks')
    type = models.IntegerField()
    content = models.JSONField()
    next = models.JSONField()


class NPC(models.Model):
    class NPCGenders(models.TextChoices):
        MALE = "male"
        FEMALE = "female"

    uid = models.CharField(max_length=7, unique=True)

    ru_name = models.CharField(max_length=31)
    en_name = models.CharField(max_length=31)

    gender = models.CharField(max_length=6, choices=NPCGenders.choices, default=NPCGenders.MALE)
    age = models.IntegerField()

    ru_description = models.TextField()
    en_description = models.TextField()

    ru_tags = models.CharField(max_length=255, blank=True)
    en_tags = models.CharField(max_length=255, blank=True)

    is_scientific_director = models.BooleanField(default=False)

    usual_image = models.ImageField(upload_to='npc_emotions')
    angry_image = models.ImageField(upload_to='npc_emotions')
    fair_image = models.ImageField(upload_to='npc_emotions')
    sad_image = models.ImageField(upload_to='npc_emotions')

    def __str__(self):
        return f"NPC[{self.uid}] {self.ru_name}"


class Location(models.Model):
    uid = models.CharField(max_length=7, unique=True)
    name = models.CharField(max_length=31)

    image = models.ImageField(upload_to='locations')
    image_disabled = models.ImageField(upload_to='locations')

    def __str__(self):
        return f"Location[{self.uid}] {self.name}"
