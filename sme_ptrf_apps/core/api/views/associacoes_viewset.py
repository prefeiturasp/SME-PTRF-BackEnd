import datetime

from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from ..serializers.associacao_serializer import AssociacaoSerializer, AssociacaoCreateSerializer

from ...models import Associacao, Periodo

from ...services import info_acoes_associacao_no_periodo


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
        ultima_atualizacao = datetime.datetime.now()
        info_acoes = info_acoes_associacao_no_periodo(associacao_uuid=uuid, periodo=periodo)
        result = {
            'associacao': f'{uuid}',
            'data_inicio_realizacao_despesas': f'{periodo.data_inicio_realizacao_despesas if periodo else ""}',
            'data_fim_realizacao_despesas': f'{periodo.data_fim_realizacao_despesas if periodo else ""}',
            'data_prevista_repasse': f'{periodo.data_prevista_repasse if periodo else ""}',
            'ultima_atualizacao': f'{ultima_atualizacao}',
            'info_acoes': info_acoes
        }

        return Response(result)
