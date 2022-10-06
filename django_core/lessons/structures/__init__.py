from enum import Enum


class LessonBlockType(Enum):
    # Блоки реплики
    replica = 100
    replicaNPC = 101

    # Обычные блоки
    theory = 202
    important = 203
    quote = 204
    image = 205
    gallery = 206
    email = 207
    browser = 208
    table = 209
    a10_doc = 210
    a12_1_messenger_start = 211
    a12_2_messenger_end = 212
    a13_downloading = 213
    a15_video = 215
    a16_button = 216
    a17_days = 217

    # блоки практики T1-T9
    radios = 301
    checkboxes = 302
    selects = 303
    input = 304
    number = 305
    radiosTable = 306
    imageAnchors = 307
    sort = 308
    comparison = 309

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class BlockType(Enum):
    lesson = 1
    quest = 2
    unit = 3
    branching = 4


class BranchingType(Enum):
    gender = 1
    six_from_n = 2
    one_from_n = 3

