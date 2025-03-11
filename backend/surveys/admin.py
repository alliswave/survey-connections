from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.urls import path
from django.http import JsonResponse

from surveys.models import Survey, Question, Answer, QuestionFlow
from surveys.inlines import AnswerInline, QuestionInline, QuestionFlowInline


class SurveyAdmin(admin.ModelAdmin):
    """Административная модель опросов"""

    list_display = ("title", "created_at", "updated_at", "is_active")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "description")
    readonly_fields = ("created_at", "updated_at")
    inlines = [QuestionInline]
    fieldsets = (
        (None, {"fields": ("title", "description", "is_active")}),
        (
            _("Информация о создании"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


class QuestionAdmin(admin.ModelAdmin):
    """Административная модель вопросов"""

    list_display = ("text", "survey", "question_type", "order", "is_required")
    list_filter = ("survey", "question_type", "is_required")
    search_fields = ("text",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [AnswerInline, QuestionFlowInline]
    fieldsets = (
        (None, {"fields": ("survey", "text", "question_type", "order", "is_required")}),
        (
            _("Информация о создании"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


class AnswerAdmin(admin.ModelAdmin):
    """Административная модель вариантов ответов"""

    list_display = ("text", "question", "order")
    list_filter = ("question__survey", "question")
    search_fields = ("text",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("question", "text", "order")}),
        (
            _("Информация о создании"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


class QuestionFlowAdmin(admin.ModelAdmin):
    """Административная модель связей между вопросами"""

    list_display = (
        "source_question",
        "relationship_type",
        "source_answer",
        "target_question",
    )
    list_filter = (
        "relationship_type",
        "source_question__survey",
        "target_question__survey",
    )
    search_fields = (
        "source_question__text",
        "target_question__text",
        "source_answer__text",
    )
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "source_question",
                    "relationship_type",
                    "source_answer",
                    "target_question",
                )
            },
        ),
        (
            _("Информация о создании"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_form(self, request, object_instance=None, **form_options):
        form_object = super().get_form(request, object_instance, **form_options)
        return form_object

    def formfield_for_foreignkey(self, database_field, request, **field_kwargs):
        if database_field.name == "source_answer":
            if request.method == "POST" and request.POST.get("source_question"):
                sourceQuestionIdentifier = request.POST.get("source_question")
                field_kwargs["queryset"] = Answer.objects.filter(
                    question_id=sourceQuestionIdentifier
                )
            elif request.resolver_match.kwargs.get("object_id"):
                questionFlowInstance = QuestionFlow.objects.get(
                    pk=request.resolver_match.kwargs.get("object_id")
                )
                if questionFlowInstance.source_question:
                    field_kwargs["queryset"] = Answer.objects.filter(
                        question=questionFlowInstance.source_question
                    )
                else:
                    field_kwargs["queryset"] = Answer.objects.none()
            else:
                field_kwargs["queryset"] = Answer.objects.none()
        return super().formfield_for_foreignkey(database_field, request, **field_kwargs)

    def get_urls(self):
        defaultUrls = super().get_urls()
        customUrls = [
            path(
                "fetch-answers/",
                self.admin_site.admin_view(self.fetch_answers),
                name="fetch_answers",
            ),
        ]
        return customUrls + defaultUrls

    def fetch_answers(self, request):
        sourceQuestionID = request.GET.get("source_question")
        if sourceQuestionID:
            answerQuerySet = Answer.objects.filter(question_id=sourceQuestionID)
            answerOptions = [
                {"id": answer.pk, "text": answer.text} for answer in answerQuerySet
            ]
        else:
            answerOptions = []
        return JsonResponse({"options": answerOptions})

    class Media:
        js = (
            "admin/js/vendor/jquery/jquery.js",
            "admin/js/question_flow_dynamic.js",
        )


admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(QuestionFlow, QuestionFlowAdmin)
