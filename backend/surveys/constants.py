from django.utils.translation import gettext_lazy as _

QUESTION_TYPE_SINGLE = "single"
QUESTION_TYPE_MULTIPLE = "multiple"
QUESTION_TYPE_TEXT = "text"

QUESTION_TYPES = [
    (QUESTION_TYPE_SINGLE, _("одиночный выбор")),
    (QUESTION_TYPE_MULTIPLE, _("множественный выбор")),
    (QUESTION_TYPE_TEXT, _("текстовый ответ")),
]

FLOW_TYPE_ANY_ANSWER = "any"
FLOW_TYPE_SPECIFIC_ANSWER = "specific"

QUESTION_FLOW_TYPES = [
    (FLOW_TYPE_ANY_ANSWER, _("любой ответ вопроса")),
    (FLOW_TYPE_SPECIFIC_ANSWER, _("конкретный ответ вопроса")),
]
