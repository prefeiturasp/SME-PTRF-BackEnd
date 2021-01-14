from datetime import datetime

from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers.periodo_serializer import PeriodoSerializer, PeriodoLookUpSerializer, PeriodoRetrieveSerializer
from ...models import Periodo


class PeriodosViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = Periodo.objects.all().order_by('-referencia')
    serializer_class = PeriodoSerializer

    def get_queryset(self):
        qs = Periodo.objects.all()

        referencia = self.request.query_params.get('referencia')
        if referencia is not None:
            qs = qs.filter(referencia__icontains=referencia)

        return qs.order_by('-referencia')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PeriodoRetrieveSerializer
        else:
            return PeriodoSerializer

    @action(detail=False)
    def lookup(self, _):
        return Response(PeriodoLookUpSerializer(self.queryset.order_by('-referencia'), many=True).data)

    @action(detail=False, url_path='lookup-until-now')
    def lookup_until_now(self, _):
        """Retorna os períodos excluindo os períodos que tem a data de inicio
        de realização de despesas maiores que a data atual."""

        return Response(PeriodoLookUpSerializer(self.queryset.filter(data_inicio_realizacao_despesas__lte=datetime.today()).order_by('-referencia'), many=True).data)
