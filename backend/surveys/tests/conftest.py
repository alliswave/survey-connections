import pytest
from rest_framework.test import APIClient
from model_bakery import baker
from django.contrib.auth.models import User

from surveys.models import QuestionFlow, Survey, Question, Answer
from surveys.constants import FLOW_TYPE_ANY_ANSWER, FLOW_TYPE_SPECIFIC_ANSWER


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client():
    client = APIClient()
    user = baker.make(User)
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def survey():
    return baker.make(Survey)


@pytest.fixture
def source_question(survey):
    return baker.make(Question, survey=survey)


@pytest.fixture
def target_question(survey):
    return baker.make(Question, survey=survey)


@pytest.fixture
def source_answer(source_question):
    return baker.make(Answer, question=source_question)


@pytest.fixture
def question_flow_data(source_question, target_question):
    return {
        "source_question": source_question.id,
        "target_question": target_question.id,
        "relationship_type": FLOW_TYPE_ANY_ANSWER,
    }


@pytest.fixture
def question_flow_with_answer_data(source_question, target_question, source_answer):
    return {
        "source_question": source_question.id,
        "target_question": target_question.id,
        "relationship_type": FLOW_TYPE_SPECIFIC_ANSWER,
        "source_answer": source_answer.id,
    }


@pytest.fixture
def question_flow(source_question, target_question):
    return baker.make(
        QuestionFlow,
        source_question=source_question,
        target_question=target_question,
        relationship_type=FLOW_TYPE_ANY_ANSWER,
    )
