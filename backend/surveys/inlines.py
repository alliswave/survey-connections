from django.contrib import admin

from surveys.models import Answer, Question, QuestionFlow


class AnswerInline(admin.TabularInline):
    """Встроенная форма для вариантов ответов вопроса"""

    model = Answer
    extra = 1
    fields = ("text", "order")


class QuestionInline(admin.StackedInline):
    """Встроенная форма для вопросов в опросе"""

    model = Question
    extra = 1
    fields = ("text", "question_type", "order", "is_required")
    inlines = [AnswerInline]
    classes = ["collapse"]


class QuestionFlowInline(admin.TabularInline):
    """Встроенная форма для связей между вопросами"""

    model = QuestionFlow
    fk_name = "source_question"
    extra = 1
    fields = ("relationship_type", "source_answer", "target_question")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Фильтрация полей выбора в зависимости от контекста"""
        question_id = None

        if hasattr(request, "resolver_match") and request.resolver_match.kwargs.get(
            "object_id"
        ):
            try:
                question_id = int(request.resolver_match.kwargs.get("object_id"))
            except (ValueError, TypeError):
                pass

        if question_id:
            if db_field.name == "source_answer":
                kwargs["queryset"] = Answer.objects.filter(question_id=question_id)
            elif db_field.name == "target_question":
                kwargs["queryset"] = Question.objects.exclude(id=question_id)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
