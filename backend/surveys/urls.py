from django.urls import path, include
from rest_framework.routers import DefaultRouter

from surveys.views import QuestionFlowViewSet

router = DefaultRouter()
router.register(r"question-flow", QuestionFlowViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
