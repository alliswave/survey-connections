from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from surveys.models import QuestionFlow
from surveys.serializers import QuestionFlowSerializer


class QuestionFlowViewSet(viewsets.ModelViewSet):
    queryset = QuestionFlow.objects.all()
    serializer_class = QuestionFlowSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
