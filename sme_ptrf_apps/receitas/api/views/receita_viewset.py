import logging

from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import AcaoAssociacaoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.conta_associacao_serializer import ContaAssociacaoLookUpSerializer
from sme_ptrf_apps.core.api.serializers.periodo_serializer import PeriodoLookUpSerializer
from sme_ptrf_apps.receitas.models import Receita
from sme_ptrf_apps.users.permissoes import PermissaoReceita, PermissaoAssociacao
from ..serializers import ReceitaCreateSerializer, ReceitaListaSerializer, TipoReceitaEDetalhesSerializer
from ...services import atualiza_repasse_para_pendente
from ...tipos_aplicacao_recurso_receitas import aplicacoes_recurso_to_json
from ....core.models import Periodo

logger = logging.getLogger(__name__)


class ReceitaViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    lookup_field = 'uuid'
    queryset = Receita.objects.all().order_by('-data')
    serializer_class = ReceitaListaSerializer
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    ordering_fields = ('data',)
    filter_fields = ('associacao__uuid', 'tipo_receita', 'acao_associacao__uuid', 'conta_associacao__uuid', 'conferido')
    permission_classes = [IsAuthenticated & PermissaoReceita]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return ReceitaListaSerializer
        else:
            return ReceitaCreateSerializer

    def get_queryset(self):
        associacao_uuid = self.request.query_params.get('associacao_uuid') or self.request.query_params.get('associacao__uuid')
        if associacao_uuid is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da associação como parâmetro.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        qs = Receita.objects.filter(associacao__uuid=associacao_uuid).all().order_by('-data')

        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        if data_inicio is not None and data_fim is not None:
            qs = qs.filter(data__range=[data_inicio, data_fim])

        search = self.request.query_params.get('search')
        if search is not None:
            qs = qs.filter(Q(detalhe_outros__unaccent__icontains=search) | Q(
                detalhe_tipo_receita__nome__unaccent__icontains=search))

        return qs

    @action(detail=False, url_path='tabelas', permission_classes=[PermissaoReceita | PermissaoAssociacao])
    def tabelas(self, request):

        associacao_uuid = request.query_params.get('associacao_uuid')

        if associacao_uuid is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da associação (associacao_uuid) como parâmetro.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        def get_valores_from(serializer, associacao_uuid):
            valores = serializer.Meta.model.get_valores(user=request.user, associacao_uuid=associacao_uuid)
            return serializer(valores, many=True).data if valores else []

        result = {
            'tipos_receita': get_valores_from(TipoReceitaEDetalhesSerializer, associacao_uuid=associacao_uuid),
            'categorias_receita': aplicacoes_recurso_to_json(),
            'acoes_associacao': get_valores_from(AcaoAssociacaoLookUpSerializer, associacao_uuid=associacao_uuid),
            'contas_associacao': get_valores_from(ContaAssociacaoLookUpSerializer, associacao_uuid=associacao_uuid),
            'periodos': get_valores_from(PeriodoLookUpSerializer, associacao_uuid=associacao_uuid),
        }

        return Response(result)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.tipo_receita.e_repasse:
            atualiza_repasse_para_pendente(instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'])
    def conciliar(self, request, uuid):
        periodo_uuid = request.query_params.get('periodo')

        if periodo_uuid is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid do período onde esta sendo feita a conciliação.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except Periodo.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)


        receita_conciliada = Receita.conciliar(uuid=uuid, periodo_conciliacao=periodo)
        return Response(ReceitaListaSerializer(receita_conciliada, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def desconciliar(self, request, uuid):
        receita_desconciliada = Receita.desconciliar(uuid=uuid)
        return Response(ReceitaListaSerializer(receita_desconciliada, many=False).data,
                        status=status.HTTP_200_OK)
