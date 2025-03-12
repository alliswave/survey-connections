from rest_framework import serializers
from surveys.models import QuestionFlow
from django.utils.translation import gettext_lazy as _


class QuestionFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionFlow
        fields = [
            "id",
            "source_question",
            "target_question",
            "relationship_type",
            "source_answer",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        relationship_type = data.get("relationship_type")
        source_answer = data.get("source_answer")
        source_question = data.get("source_question")
        target_question = data.get("target_question")

        if source_question == target_question:
            raise serializers.ValidationError(
                _("Исходный и целевой вопросы не могут быть одинаковыми")
            )

        if relationship_type == "specific_answer" and not source_answer:
            raise serializers.ValidationError(
                _("Для типа связи 'конкретный ответ' требуется указать исходный ответ")
            )

        if source_answer and source_answer.question != source_question:
            raise serializers.ValidationError(
                _("Исходный ответ должен принадлежать исходному вопросу")
            )

        return data
