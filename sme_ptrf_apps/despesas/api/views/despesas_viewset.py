from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.db.models.query import QuerySet

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
)

from ....core.api.serializers import TagLookupSerializer
from ....core.api.serializers.acao_associacao_serializer import AcaoAssociacaoLookUpSerializer
from ....core.api.serializers.conta_associacao_serializer import ContaAssociacaoLookUpSerializer
from ...models import Despesa
from ...tipos_aplicacao_recurso import aplicacoes_recurso_to_json
from ..serializers.despesa_serializer import DespesaCreateSerializer, DespesaListSerializer, DespesaSerializer
from ..serializers.tipo_custeio_serializer import TipoCusteioSerializer
from ..serializers.tipo_documento_serializer import TipoDocumentoSerializer
from ..serializers.tipo_transacao_serializer import TipoTransacaoSerializer


class DespesasViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Despesa.objects.all()
    serializer_class = DespesaSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = (
    'associacao__uuid', 'cpf_cnpj_fornecedor', 'tipo_documento__uuid', 'numero_documento', 'tipo_documento__id')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DespesaSerializer
        elif self.action == 'list':
            return DespesaListSerializer
        else:
            return DespesaCreateSerializer

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError
        from ....core.models import DevolucaoAoTesouro

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError as exception:

            erros = []

            if exception.args:
                for excecao in exception.args:
                    if isinstance(excecao, QuerySet):
                        for ex in excecao:
                            if isinstance(ex, DevolucaoAoTesouro):
                                erros.append(f'{ex._meta.verbose_name}: {ex.data.strftime("%d/%m/%Y") if ex.data else "Sem data"} - {ex.tipo}')
                            else:
                                erros.append(f'{ex._meta.verbose_name}: {ex}')

            content = {
                'code': 'server_error',
                'message': 'Internal server error.',
                'error': {
                    'type': str(type(exception)),
                    'message': str(exception),
                    'itens_erro': erros
                }
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='tabelas',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
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
            'tipos_aplicacao_recurso': aplicacoes_recurso_to_json(),
            'tipos_custeio': get_valores_from(TipoCusteioSerializer, associacao_uuid=associacao_uuid),
            'tipos_documento': get_valores_from(TipoDocumentoSerializer, associacao_uuid=associacao_uuid),
            'tipos_transacao': get_valores_from(TipoTransacaoSerializer, associacao_uuid=associacao_uuid),
            'acoes_associacao': get_valores_from(AcaoAssociacaoLookUpSerializer, associacao_uuid=associacao_uuid),
            'contas_associacao': get_valores_from(ContaAssociacaoLookUpSerializer, associacao_uuid=associacao_uuid),
            'tags': get_valores_from(TagLookupSerializer, associacao_uuid=associacao_uuid),
        }

        return Response(result)

    @action(detail=False, url_path='ja-lancada',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def ja_lancada(self, request):

        tipo_documento = request.query_params.get('tipo_documento')

        if tipo_documento is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar a o id do tipo de documento como parâmetro. Ex: tipo_documento=1.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        numero_documento = request.query_params.get('numero_documento')
        if numero_documento is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar a o número do documento como parâmetro. Ex: numero_documento=123.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        cpf_cnpj_fornecedor = request.query_params.get('cpf_cnpj_fornecedor')
        if cpf_cnpj_fornecedor is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar a o número do documento como parâmetro. Ex: cpf_cnpj_fornecedor=455..'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        associacao__uuid = request.query_params.get('associacao__uuid')
        if associacao__uuid is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar a o uuid da associação como parâmetro. Ex: associacao__uuid=GSDHH3434..'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        despesa_uuid = request.query_params.get('despesa_uuid')

        despesa = Despesa.by_documento(tipo_documento=tipo_documento, numero_documento=numero_documento,
                                       cpf_cnpj_fornecedor=cpf_cnpj_fornecedor, associacao__uuid=associacao__uuid)

        despesa_ja_lancada = despesa is not None and f'{despesa.uuid}' != despesa_uuid

        result = {
            'despesa_ja_lancada': despesa_ja_lancada,
            'uuid_despesa': f'{despesa.uuid}' if despesa_ja_lancada else ''
        }

        return Response(result)
