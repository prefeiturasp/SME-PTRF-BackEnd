import datetime

from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers.associacao_serializer import AssociacaoSerializer, AssociacaoCreateSerializer
from ...models import Associacao, Periodo
from ...services import (info_acoes_associacao_no_periodo, status_periodo_associacao,
                         status_aceita_alteracoes_em_transacoes)


class AssociacoesViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         GenericViewSet):
    permission_classes = [AllowAny]
    lookup_field = 'uuid'
    queryset = Associacao.objects.all()
    serializer_class = AssociacaoSerializer

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return AssociacaoSerializer
        else:
            return AssociacaoCreateSerializer

    @action(detail=True, url_path='painel-acoes')
    def painel_acoes(self, request, uuid=None):

        periodo = Periodo.periodo_atual()
        periodo_status = status_periodo_associacao(periodo_uuid=periodo.uuid, associacao_uuid=uuid)
        ultima_atualizacao = datetime.datetime.now()
        info_acoes = info_acoes_associacao_no_periodo(associacao_uuid=uuid, periodo=periodo)

        result = {
            'associacao': f'{uuid}',
            'periodo_referencia': periodo.referencia,
            'periodo_status': periodo_status,
            'data_inicio_realizacao_despesas': f'{periodo.data_inicio_realizacao_despesas if periodo else ""}',
            'data_fim_realizacao_despesas': f'{periodo.data_fim_realizacao_despesas if periodo else ""}',
            'data_prevista_repasse': f'{periodo.data_prevista_repasse if periodo else ""}',
            'ultima_atualizacao': f'{ultima_atualizacao}',
            'info_acoes': info_acoes
        }

        return Response(result)

    @action(detail=True, url_path='status-periodo')
    def status_periodo(self, request, uuid=None):

        data = request.query_params.get('data')

        if data is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar a data que você quer consultar o status.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        periodo = Periodo.da_data(data)
        periodo_status = status_periodo_associacao(periodo_uuid=periodo.uuid, associacao_uuid=uuid)
        aceita_alteracoes = status_aceita_alteracoes_em_transacoes(periodo_status)

        result = {
            'associacao': f'{uuid}',
            'periodo_referencia': periodo.referencia,
            'periodo_status': periodo_status,
            'aceita_alteracoes': aceita_alteracoes,
        }

        return Response(result)
