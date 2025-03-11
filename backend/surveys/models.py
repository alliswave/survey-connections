from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from core.models import TimeStampedModel
from surveys.constants import (
    QUESTION_TYPE_SINGLE,
    QUESTION_TYPES,
    FLOW_TYPE_ANY_ANSWER,
    FLOW_TYPE_SPECIFIC_ANSWER,
    QUESTION_FLOW_TYPES,
)


class Survey(TimeStampedModel):
    """Модель для представления опроса"""

    title = models.CharField(_("название"), max_length=255)
    description = models.TextField(_("описание"), blank=True)
    is_active = models.BooleanField(_("активен"), default=True)

    class Meta:
        verbose_name = _("опрос")
        verbose_name_plural = _("опросы")

    def __str__(self):
        return self.title


class Question(TimeStampedModel):
    """Модель для представления вопроса в опросе"""

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("опрос"),
    )
    text = models.TextField(_("текст вопроса"))
    question_type = models.CharField(
        _("тип вопроса"),
        max_length=20,
        choices=QUESTION_TYPES,
        default=QUESTION_TYPE_SINGLE,
    )
    order = models.PositiveIntegerField(_("порядок"), default=0)
    is_required = models.BooleanField(_("обязательный"), default=True)

    class Meta:
        verbose_name = _("вопрос")
        verbose_name_plural = _("вопросы")
        ordering = ["order"]

    def __str__(self):
        return self.text


class Answer(TimeStampedModel):
    """Модель для представления варианта ответа на вопрос"""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("вопрос"),
    )
    text = models.CharField(_("текст ответа"), max_length=255)
    order = models.PositiveIntegerField(_("порядок"), default=0)

    class Meta:
        verbose_name = _("вариант ответа")
        verbose_name_plural = _("варианты ответов")
        ordering = ["order"]

    def __str__(self):
        return self.text


class QuestionFlow(TimeStampedModel):
    """Модель для связи между вопросами на основе ответов"""

    source_question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="source_relationships",
        verbose_name=_("исходный вопрос"),
    )
    target_question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="target_relationships",
        verbose_name=_("целевой вопрос"),
    )
    relationship_type = models.CharField(
        _("тип связи"),
        max_length=20,
        choices=QUESTION_FLOW_TYPES,
        default=FLOW_TYPE_ANY_ANSWER,
    )
    source_answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="triggered_relationships",
        verbose_name=_("исходный ответ"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("связь вопросов")
        verbose_name_plural = _("связи вопросов")
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "source_question",
                    "target_question",
                    "relationship_type",
                    "source_answer",
                ],
                name="unique_question_flow",
            ),
            models.UniqueConstraint(
                fields=["source_question", "target_question"],
                condition=models.Q(relationship_type=FLOW_TYPE_ANY_ANSWER),
                name="unique_any_answer_flow",
            ),
        ]

    def __str__(self):
        if self.relationship_type == FLOW_TYPE_ANY_ANSWER:
            return _('Любой ответ на "{source}" ведёт к "{target}"').format(
                source=self.source_question, target=self.target_question
            )
        else:
            return _('Ответ "{answer}" на "{source}" ведёт к "{target}"').format(
                answer=self.source_answer,
                source=self.source_question,
                target=self.target_question,
            )

    def clean(self):
        if (
            self.relationship_type == FLOW_TYPE_SPECIFIC_ANSWER
            and self.source_answer is None
        ):
            raise ValidationError(
                _("Для связи по конкретному ответу необходимо указать ответ")
            )

        if self.source_answer and self.source_answer.question != self.source_question:
            raise ValidationError(
                _("Выбранный ответ должен принадлежать исходному вопросу")
            )

        if self.source_question == self.target_question:
            raise ValidationError(_("Исходный и целевой вопросы не могут совпадать"))

        # Проверяем уникальность связи с учетом всех особенностей
        existing_flows = QuestionFlow.objects.filter(
            source_question=self.source_question,
            target_question=self.target_question,
            relationship_type=self.relationship_type,
        )

        # Исключаем текущий объект при редактировании
        if self.pk:
            existing_flows = existing_flows.exclude(pk=self.pk)

        # Для связи на основе конкретного ответа проверяем по source_answer
        if (
            self.relationship_type == FLOW_TYPE_SPECIFIC_ANSWER
            and existing_flows.filter(source_answer=self.source_answer).exists()
        ):
            raise ValidationError(_("Такая связь уже существует"))

        # Для связи на основе любого ответа - просто проверяем наличие
        if self.relationship_type == FLOW_TYPE_ANY_ANSWER and existing_flows.exists():
            raise ValidationError(_("Связь между этими вопросами уже существует"))
