from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.models import RelacaoBens


class RelacaoBensViewSet(GenericViewSet):
    permission_classes = [AllowAny]
    queryset = RelacaoBens.objects.all()

    @action(detail=False, methods=['get'])
    def previa(self, request):
        return Response("Hello Relação de bens")
