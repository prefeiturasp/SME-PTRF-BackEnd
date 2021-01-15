from datetime import datetime

from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers.periodo_serializer import (PeriodoSerializer, PeriodoLookUpSerializer, PeriodoRetrieveSerializer,
                                              PeriodoCreateSerializer)
from ...models import Periodo
from ...services import valida_datas_periodo


class PeriodosViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
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
        elif self.action == 'create':
            return PeriodoCreateSerializer
        else:
            return PeriodoSerializer

    @action(detail=False)
    def lookup(self, _):
        return Response(PeriodoLookUpSerializer(self.queryset.order_by('-referencia'), many=True).data)

    @action(detail=False, url_path='lookup-until-now')
    def lookup_until_now(self, _):
        """Retorna os períodos excluindo os períodos que tem a data de inicio
        de realização de despesas maiores que a data atual."""

        return Response(PeriodoLookUpSerializer(
            self.queryset.filter(data_inicio_realizacao_despesas__lte=datetime.today()).order_by('-referencia'),
            many=True).data)

    @action(detail=False, url_path='verificar-datas')
    def verificar_datas(self, request):
        """Recebe um payload com as datas (inicial e final) de realização de despesas e
        o uuid do período anterior (se houver) e verifica se as datas de realização de
        despesa são válidas conforme as regras de negócio."""

        data_inicio_realizacao_despesas = request.query_params.get('data_inicio_realizacao_despesas', None)
        if not data_inicio_realizacao_despesas:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'verificar-datas',
                'mensagem': 'Faltou informar a data de inicio de realização de despesas. ?data_inicio_realizacao_despesas= '
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        data_fim_realizacao_despesas = request.query_params.get('data_fim_realizacao_despesas', None)
        if not data_fim_realizacao_despesas:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'verificar-datas',
                'mensagem': 'Faltou informar a data de fim da realização de despesas. ?data_fim_realizacao_despesas= '
            }

            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        periodo_anterior_uuid = request.query_params.get('periodo_anterior_uuid', None)

        if periodo_anterior_uuid:
            try:
                periodo_anterior = Periodo.objects.get(uuid=periodo_anterior_uuid)
            except Periodo.DoesNotExist:
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto periodo para o uuid {periodo_anterior_uuid} não foi encontrado na base."
                }

                return Response(erro, status=status.HTTP_400_BAD_REQUEST)
        else:
            periodo_anterior = None

        result = valida_datas_periodo(
            data_inicio_realizacao_despesas=datetime.strptime(data_inicio_realizacao_despesas, '%Y-%m-%d').date(),
            data_fim_realizacao_despesas=datetime.strptime(data_fim_realizacao_despesas, '%Y-%m-%d').date(),
            periodo_anterior=periodo_anterior
        )

        return Response(result)
