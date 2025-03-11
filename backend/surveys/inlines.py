import re
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from surveys.models import Answer, Question, QuestionFlow


class AnswerInline(admin.TabularInline):
    """Встроенная форма для вариантов ответов вопроса"""
    model = Answer
    extra = 1
    fields = ('text', 'order')


class QuestionInline(admin.StackedInline):
    """Встроенная форма для вопросов в опросе"""
    model = Question
    extra = 1
    fields = ('text', 'question_type', 'order', 'is_required')
    inlines = [AnswerInline]
    classes = ['collapse']


class QuestionFlowInline(admin.TabularInline):
    """Встроенная форма для связей между вопросами"""
    model = QuestionFlow
    fk_name = 'source_question'
    extra = 1
    fields = ('relationship_type', 'source_answer', 'target_question')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Фильтрация полей выбора в зависимости от контекста"""
        # Находим ID вопроса из URL или объекта
        question_id = None
        
        # Для существующего вопроса (редактирование)
        if hasattr(request, 'resolver_match') and request.resolver_match.kwargs.get('object_id'):
            try:
                # Пытаемся получить ID вопроса из URL
                question_id = int(request.resolver_match.kwargs.get('object_id'))
            except (ValueError, TypeError):
                pass
        
        # Применяем фильтрацию, если знаем ID вопроса
        if question_id:
            if db_field.name == "source_answer":
                # Фильтруем ответы только текущим вопросом
                kwargs["queryset"] = Answer.objects.filter(question_id=question_id)
            elif db_field.name == "target_question":
                # Исключаем текущий вопрос из целевых
                kwargs["queryset"] = Question.objects.exclude(id=question_id)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)