from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers.periodo_serializer import PeriodoSerializer, PeriodoLookUpSerializer
from ...models import Periodo


class PeriodosViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      GenericViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = Periodo.objects.all().order_by('-referencia')
    serializer_class = PeriodoSerializer

    @action(detail=False)
    def lookup(self, _):
        return Response(PeriodoLookUpSerializer(self.queryset.order_by('-referencia'), many=True).data)
