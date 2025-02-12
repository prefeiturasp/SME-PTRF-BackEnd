from datetime import datetime

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins, status
from django.db.models import Q

from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoAPITodosComLeituraOuGravacao, PermissaoApiSME

from ...models import Repasse
from ...models.repasse import StatusRepasse
from ....core.models import Periodo, TipoConta, Acao

from ..serializers import RepasseSerializer, RepasseCreateSerializer, RepasseListSerializer
from ....core.api.serializers import PeriodoSerializer, TipoContaSerializer, AcaoSerializer, ContaAssociacaoLookUpSerializer, AcaoAssociacaoLookUpSerializer
from ....core.api.utils.pagination import CustomPagination


class RepasseViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):
    lookup_field = 'uuid'
    queryset = Repasse.objects.all().order_by('id')
    permission_classes = [IsAuthenticated & (PermissaoApiUe | PermissaoApiSME)]
    serializer_class = RepasseSerializer
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RepasseListSerializer
        elif self.action == 'list':
            return RepasseListSerializer
        else:
            return RepasseCreateSerializer

    def get_queryset(self):
        qs = Repasse.objects.all().order_by('-periodo__referencia')

        search = self.request.query_params.get('search')
        if search is not None:
            qs = qs.filter(
                Q(associacao__unidade__codigo_eol=search) |
                Q(associacao__nome__unaccent__icontains=search) |
                Q(associacao__unidade__nome__unaccent__icontains=search)
            )

        periodo_uuid = self.request.query_params.get('periodo')
        if periodo_uuid is not None and periodo_uuid != "":
            qs = qs.filter(periodo__uuid=periodo_uuid)

        conta_uuid = self.request.query_params.get('conta')
        if conta_uuid is not None and conta_uuid != "":
            qs = qs.filter(conta_associacao__tipo_conta__uuid=conta_uuid)

        acao_uuid = self.request.query_params.get('acao')
        if acao_uuid is not None and acao_uuid != "":
            qs = qs.filter(acao_associacao__acao__uuid=acao_uuid)

        status = self.request.query_params.get('status')
        if status is not None and status != "":
            qs = qs.filter(status=status)

        return qs

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        if obj.status == StatusRepasse.REALIZADO.name:
            content = {
                'erro': 'StatusNaoPermitido',
                'mensagem': 'Não é possível excluir um repasse realizado.'
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if obj.possui_receita_vinculada:
            content = {
                'erro': 'ReceitaVinculada',
                'mensagem': 'Não é possível excluir um repasse com crédito vinculado.'
            }

            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Não é possível excluir esse repasse porque ele já possui movimentação.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def pendentes(self, request, *args, **kwargs):
        associacao_uuid = self.request.query_params.get('associacao')

        if not associacao_uuid:
            return Response("uuid da associação é obrigatório.", status=HTTP_400_BAD_REQUEST)

        repasses = Repasse.objects\
            .filter(
                associacao__uuid=associacao_uuid,
                status='PENDENTE')\
            .order_by('-criado_em').all()

        serializer = RepasseSerializer(repasses, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def tabelas(self, request):
        
        periodos_ordenados = Periodo.objects.all().order_by('-referencia')

        result = {
            "periodos": PeriodoSerializer(periodos_ordenados, many=True).data,
            "tipos_contas": TipoContaSerializer(TipoConta.objects.all(), many=True).data,
            "acoes": AcaoSerializer(Acao.objects.all(), many=True).data,
            "status": Repasse.status_to_json()
        }

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='tabelas-por-associacao',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def tabelas_por_associacao(self, request):

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
            'acoes_associacao': get_valores_from(AcaoAssociacaoLookUpSerializer, associacao_uuid=associacao_uuid),
            'contas_associacao': get_valores_from(ContaAssociacaoLookUpSerializer, associacao_uuid=associacao_uuid),
        }

        return Response(result)
