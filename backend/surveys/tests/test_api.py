import pytest
from django.urls import reverse
from rest_framework import status
from model_bakery import baker

from surveys.models import QuestionFlow, Question, Answer
from surveys.constants import (
    FLOW_TYPE_ANY_ANSWER,
    FLOW_TYPE_SPECIFIC_ANSWER,
)


@pytest.mark.django_db
class TestQuestionFlowAPI:
    def test_list_question_flows_unauthenticated(self, api_client):
        url = reverse("questionflow-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_question_flows_authenticated(
        self, authenticated_client, question_flow
    ):
        url = reverse("questionflow-list")
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_retrieve_question_flow(self, authenticated_client, question_flow):
        url = reverse("questionflow-detail", kwargs={"pk": question_flow.id})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == question_flow.id

    def test_create_question_flow_success(
        self, authenticated_client, question_flow_data
    ):
        url = reverse("questionflow-list")
        response = authenticated_client.post(url, question_flow_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert QuestionFlow.objects.count() == 1

    def test_create_question_flow_with_answer_success(
        self, authenticated_client, question_flow_with_answer_data
    ):
        url = reverse("questionflow-list")
        response = authenticated_client.post(
            url, question_flow_with_answer_data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert QuestionFlow.objects.count() == 1
        assert QuestionFlow.objects.first().source_answer is not None

    def test_create_question_flow_same_questions_error(
        self, authenticated_client, source_question
    ):
        url = reverse("questionflow-list")
        data = {
            "source_question": source_question.id,
            "target_question": source_question.id,
            "relationship_type": FLOW_TYPE_ANY_ANSWER,
        }
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_question_flow_missing_answer_error(
        self, authenticated_client, source_question, target_question
    ):
        url = reverse("questionflow-list")
        data = {
            "source_question": source_question.id,
            "target_question": target_question.id,
            "relationship_type": FLOW_TYPE_SPECIFIC_ANSWER,
        }
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_question_flow_wrong_answer_error(
        self, authenticated_client, source_question, target_question
    ):
        wrong_answer = baker.make(Answer, question=target_question)
        url = reverse("questionflow-list")
        data = {
            "source_question": source_question.id,
            "target_question": target_question.id,
            "relationship_type": FLOW_TYPE_SPECIFIC_ANSWER,
            "source_answer": wrong_answer.id,
        }
        response = authenticated_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_question_flow(
        self, authenticated_client, question_flow, target_question
    ):
        new_target = baker.make(Question, survey=target_question.survey)
        url = reverse("questionflow-detail", kwargs={"pk": question_flow.id})
        data = {
            "source_question": question_flow.source_question.id,
            "target_question": new_target.id,
            "relationship_type": question_flow.relationship_type,
        }
        response = authenticated_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        question_flow.refresh_from_db()
        assert question_flow.target_question.id == new_target.id

    def test_partial_update_question_flow(
        self, authenticated_client, question_flow, target_question
    ):
        new_target = baker.make(Question, survey=target_question.survey)
        url = reverse("questionflow-detail", kwargs={"pk": question_flow.id})
        data = {"target_question": new_target.id}
        response = authenticated_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        question_flow.refresh_from_db()
        assert question_flow.target_question.id == new_target.id

    def test_delete_question_flow(self, authenticated_client, question_flow):
        url = reverse("questionflow-detail", kwargs={"pk": question_flow.id})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert QuestionFlow.objects.count() == 0
