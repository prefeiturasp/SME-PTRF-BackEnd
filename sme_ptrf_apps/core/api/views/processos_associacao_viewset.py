from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from sme_ptrf_apps.core.api.serializers import (
    ProcessoAssociacaoCreateSerializer,
    ProcessoAssociacaoRetrieveSerializer,
    PeriodoLookUpSerializer)
from sme_ptrf_apps.core.models import ProcessoAssociacao, Periodo
from sme_ptrf_apps.users.permissoes import PermissaoApiDre


class ProcessosAssociacaoViewSet(mixins.RetrieveModelMixin,
                                 mixins.CreateModelMixin,
                                 mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin,
                                 GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    serializer_class = ProcessoAssociacaoRetrieveSerializer
    queryset = ProcessoAssociacao.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProcessoAssociacaoRetrieveSerializer
        else:
            return ProcessoAssociacaoCreateSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.e_o_ultimo_processo_do_ano_com_pcs_vinculada:
            msg = {
                'erro': 'possui_prestacao_de_conta_vinculada',
                'mensagem': ('Não é possível excluir o número desse processo SEI, pois este já está vinculado a'
                             ' uma prestação de contas. Caso necessário, é possível editá-lo.')
            }
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        # Define os parâmetros que a action aceita
        parameters=[
            OpenApiParameter(name='associacao_uuid', description='UUID da Associação', required=True,
                             type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='processo_uuid',
                             description='UUID do Processo de Associação (opcional para novos processos)',
                             required=False, type=OpenApiTypes.UUID, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='ano', description='Ano dos Períodos a serem retornados', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: PeriodoLookUpSerializer(many=True)},
        description="Retorna todos os períodos do ano que podem ser vinculados ao processo, "
                    "considerando se é uma inclusão de novo processo ou uma atualização."
    )
    @action(detail=False, methods=['get'], url_path='periodos-disponiveis')
    def periodos_disponiveis(self, request):
        associacao_uuid = request.query_params.get('associacao_uuid')
        processo_uuid = request.query_params.get('processo_uuid')
        ano = request.query_params.get('ano')

        if not associacao_uuid or not ano:
            return Response({"erro": "Os parâmetros 'associacao_uuid' e 'ano' são obrigatórios."}, status=400)

        periodos_query = Periodo.objects.filter(referencia__startswith=ano)

        # Identifica todos os períodos já vinculados a processos para a associação especificada,
        # Excluindo o próprio processo se um UUID foi fornecido.
        processos_associacao_query = ProcessoAssociacao.objects.filter(associacao__uuid=associacao_uuid)
        if processo_uuid:
            processos_associacao_query = processos_associacao_query.exclude(uuid=processo_uuid)

        # Exclui os períodos já vinculados a outros processos da associação.
        periodos_ja_vinculados = [uuid for uuid in processos_associacao_query.values_list(
            'periodos__uuid', flat=True).distinct() if uuid is not None]
        periodos_disponiveis = periodos_query.exclude(uuid__in=periodos_ja_vinculados)

        serializer = PeriodoLookUpSerializer(periodos_disponiveis, many=True)
        return Response(serializer.data)
