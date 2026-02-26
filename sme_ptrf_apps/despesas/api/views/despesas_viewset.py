from django_filters import rest_framework as filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.db.models.query import QuerySet
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse
from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.despesas.services.filtra_despesas_por_tags import filtra_despesas_por_tags

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe,
    PermissaoAPITodosComLeituraOuGravacao,
)

from ....core.api.serializers import TagLookupSerializer
from ....core.api.serializers.acao_associacao_serializer import AcaoAssociacaoLookUpSerializer
from ....core.api.serializers.conta_associacao_serializer import ContaAssociacaoLookUpSerializer
from ...models import Despesa
from ...tipos_aplicacao_recurso import aplicacoes_recurso_to_json
from ..serializers.despesa_serializer import DespesaCreateSerializer, DespesaSerializer, DespesaListComRateiosSerializer
from ..serializers.tipo_custeio_serializer import TipoCusteioSerializer
from ..serializers.tipo_documento_serializer import TipoDocumentoSerializer
from ..serializers.tipo_transacao_serializer import TipoTransacaoSerializer
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from django.db.models import Subquery
from sme_ptrf_apps.core.models import Associacao
from django.db.models import Q
import datetime

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10


class CustomPagination(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'page': int(self.request.GET.get('page', DEFAULT_PAGE)),
            'page_size': int(self.request.GET.get('page_size', self.page_size)),
            'results': data
        })


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
    filter_backends = (filters.DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ('associacao__uuid', 'cpf_cnpj_fornecedor', 'tipo_documento__uuid',
                        'numero_documento', 'tipo_documento__id', 'status')
    pagination_class = CustomPagination

    def get_queryset(self):
        from ...services.despesa_service import ordena_despesas_por_imposto
        qs = Despesa.objects.exclude(status='INATIVO').all()
        for item in qs:
            print(item.recurso)
        print(self.request.recurso)
        qs = Despesa.filter_by_recurso(qs, self.request.recurso)

        search = self.request.query_params.get('search')
        if search is not None and search != '':
            qs = qs.filter(
                pk__in=Subquery(
                    qs.filter(
                        rateios__especificacao_material_servico__descricao__unaccent__icontains=search
                    ).distinct("uuid").values('pk')
                )
            )

        tag_uuid = self.request.query_params.get('rateios__tag__uuid')
        if tag_uuid:
            # Necessario para utilizar distinct e order by juntos, com valores diferentes
            qs = qs.filter(
                pk__in=Subquery(
                    qs.filter(rateios__tag__uuid=tag_uuid).distinct("uuid").values('pk')
                )
            )

        acao_associacao_uuid = self.request.query_params.get('rateios__acao_associacao__uuid')

        if acao_associacao_uuid:
            # Necessario para utilizar distinct e order by juntos, com valores diferentes
            qs = qs.filter(
                pk__in=Subquery(
                    qs.filter(rateios__acao_associacao__uuid=acao_associacao_uuid).distinct("uuid").values('pk')
                )
            )

        aplicacao_recurso = self.request.query_params.get('aplicacao_recurso')

        if aplicacao_recurso:
            # Necessario para utilizar distinct e order by juntos, com valores diferentes
            qs = qs.filter(
                pk__in=Subquery(
                    qs.filter(rateios__aplicacao_recurso=aplicacao_recurso).distinct("uuid").values('pk')
                )
            )

        fornecedor = self.request.query_params.get('fornecedor')

        if fornecedor is not None and fornecedor != '':
            if fornecedor:
                qs = qs.filter(
                    Q(nome_fornecedor__unaccent__icontains=fornecedor) |
                    Q(cpf_cnpj_fornecedor__icontains=fornecedor)
                )
        conta_associacao__uuid = self.request.query_params.get('rateios__conta_associacao__uuid')

        if conta_associacao__uuid:
            # Necessario para utilizar distinct e order by juntos, com valores diferentes
            qs = qs.filter(
                pk__in=Subquery(
                    qs.filter(rateios__conta_associacao__uuid=conta_associacao__uuid).distinct("uuid").values('pk')
                )
            )

        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')

        if data_inicio is not None and data_fim is not None and data_inicio != '' and data_fim != '':
            qs = qs.filter(data_documento__range=[data_inicio, data_fim])
        elif data_inicio is not None and data_inicio != '':
            qs = qs.filter(data_documento__gte=data_inicio)
        elif data_fim is not None and data_fim != '':
            qs = qs.filter(data_documento__lte=data_fim)

        periodo = self.request.query_params.get('periodo__uuid')

        if periodo is not None and periodo != '':
            periodo_obj = Periodo.objects.get(uuid=periodo)
            filtros = {
                'data_transacao__gte': periodo_obj.data_inicio_realizacao_despesas,
            }

            if periodo_obj.data_fim_realizacao_despesas:
                filtros['data_transacao__lte'] = periodo_obj.data_fim_realizacao_despesas

            qs = qs.filter(**filtros)

        assoc_uuid = self.request.query_params.get('associacao__uuid')
        if assoc_uuid is not None:
            qs = qs.filter(associacao__uuid=assoc_uuid).all()

        filtro_vinculo_atividades = self.request.query_params.get('filtro_vinculo_atividades')
        filtro_vinculo_atividades_list = filtro_vinculo_atividades.split(',') if filtro_vinculo_atividades else []

        if filtro_vinculo_atividades_list:
            qs = qs.filter(
                pk__in=Subquery(
                    qs.filter(rateios__tag__id__in=filtro_vinculo_atividades_list).distinct("uuid").values('pk')
                )
            )

        filtro_informacoes = self.request.query_params.get('filtro_informacoes')
        filtro_informacoes_list = filtro_informacoes.split(',') if filtro_informacoes else []

        if filtro_informacoes_list:
            ids_para_excluir = [despesa.id for despesa in qs if filtra_despesas_por_tags(
                despesa, filtro_informacoes_list, False)]
            qs = qs.exclude(id__in=ids_para_excluir)

        # Ordenação
        ordenar_por_numero_do_documento = self.request.query_params.get('ordenar_por_numero_do_documento')
        ordenar_por_data_especificacao = self.request.query_params.get('ordenar_por_data_especificacao')
        ordenar_por_valor = self.request.query_params.get('ordenar_por_valor')
        ordenar_por_imposto = self.request.query_params.get('ordenar_por_imposto')

        lista_argumentos_ordenacao = []
        if ordenar_por_numero_do_documento and ordenar_por_numero_do_documento == 'crescente':
            lista_argumentos_ordenacao.append('numero_documento')

        if ordenar_por_numero_do_documento and ordenar_por_numero_do_documento == 'decrescente':
            lista_argumentos_ordenacao.append('-numero_documento')

        if ordenar_por_data_especificacao and ordenar_por_data_especificacao == 'crescente':
            lista_argumentos_ordenacao.append('data_documento')

        if ordenar_por_data_especificacao and ordenar_por_data_especificacao == 'decrescente':
            lista_argumentos_ordenacao.append('-data_documento')

        if ordenar_por_valor and ordenar_por_valor == 'crescente':
            lista_argumentos_ordenacao.append('valor_total')

        if ordenar_por_valor and ordenar_por_valor == 'decrescente':
            lista_argumentos_ordenacao.append('-valor_total')

        if ordenar_por_imposto == 'true':
            # Cria uma lista com os impostos ordenados. Passo os demais argumentos de ordenação e
            # já retorna ordenada por todos
            qs = ordena_despesas_por_imposto(qs, lista_argumentos_ordenacao)

            # Cria uma lista com os ids dos importos ordenados na ordem correta
            pk_list = [obj.pk for obj in qs]

            # Converte a lista de impostos em um queryset respeitando a ordem da lista
            clauses = ' '.join(['WHEN despesas_despesa.id=%s THEN %s' % (pk, i) for i, pk in enumerate(pk_list)])
            ordering = 'CASE %s END' % clauses
            qs = Despesa.objects.filter(pk__in=pk_list).extra(
                select={'ordering': ordering}, order_by=('ordering',))

        # Caso nenhum argumento de ordenação seja passado, ordenamos por -data_documento
        if not ordenar_por_imposto == 'true':
            # Caso tenha sido solicitado ordenar por imposto já
            # é retornada ordenada por todos os argumentos, além do imposto
            if not lista_argumentos_ordenacao:
                qs = qs.order_by('-data_documento', 'id')
            else:
                qs = qs.order_by(*lista_argumentos_ordenacao, 'id')

        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if self.action == "create":
            context["recurso"] = self.request.recurso

        return context

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DespesaSerializer
        elif self.action == 'list':
            return DespesaListComRateiosSerializer
        else:
            return DespesaCreateSerializer

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError
        from ....core.models import DevolucaoAoTesouro, ContaAssociacao
        despesa = self.get_object()

        if despesa.rateios.filter(conta_associacao__status=ContaAssociacao.STATUS_INATIVA).exists():
            erro = {
                'erro': 'rateio_com_conta_status_inativa',
                'mensagem': ('Não é permitido deletar despesa com rateios com conta associação'
                             f'status {ContaAssociacao.STATUS_INATIVA}')
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if not despesa.inativar_em_vez_de_excluir:
            # Em caso de inativação, a inativação dos impostos é feita pelo próprio método inativar_despesa.
            for despesa_imposto in despesa.despesas_impostos.all():
                try:
                    self.perform_destroy(despesa_imposto)
                except Exception as err:
                    erro = {
                        'erro': 'despesa_do_imposto_nao_deletada',
                        'mensagem': str(err)
                    }
                    return Response(erro, status=status.HTTP_404_NOT_FOUND)

        if despesa.inativar_em_vez_de_excluir:
            despesa.inativar_despesa()
            msg = {
                'sucesso': 'despesa_inativada_com_sucesso',
                'mensagem': 'Despesa inativada com sucesso'
            }
            return Response(msg, status=status.HTTP_200_OK)
        else:
            try:
                self.perform_destroy(despesa)
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ProtectedError as exception:
                erros = []

                if exception.args:
                    for excecao in exception.args:
                        if isinstance(excecao, QuerySet):
                            for ex in excecao:
                                if isinstance(ex, DevolucaoAoTesouro):
                                    err = '{}: {} - {}'.format(
                                        ex._meta.verbose_name,
                                        ex.data.strftime("%d/%m/%Y") if ex.data else "Sem data",
                                        ex.tipo
                                    )
                                    erros.append(err)
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

    @extend_schema(
        parameters=[
            OpenApiParameter(name='associacao_uuid', description='UUID da Associação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiResponse(
            response={
                'type': 'object',
                'properties': {
                    'tipos_aplicacao_recurso': {'type': 'object'},
                    'tipos_custeio': {'type': 'object'},
                    'tipos_documento': {'type': 'object'},
                    'tipos_transacao': {'type': 'object'},
                    'acoes_associacao': {'type': 'object'},
                    'contas_associacao': {'type': 'object'},
                    'tags': {'type': 'object'},
                },
            }
        )},
        description="Retorna tabela de dados relacionados as associações, conforme parâmetro do endpoint."
    )
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
            model = serializer.Meta.model

            valores = model.get_valores(
                user=request.user,
                associacao_uuid=associacao_uuid
            )

            if self.request.recurso and hasattr(model, "filter_by_recurso"):
                valores = model.filter_by_recurso(valores, self.request.recurso)

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

    @extend_schema(
        parameters=[
            OpenApiParameter(name='tipo_documento', description='ID do tipo de documento', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='numero_documento', description='Número de documento', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='cpf_cnpj_fornecedor', description='CPF/CNPJ do Fornecedor', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='associacao__uuid', description='UUID da Associação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='despesa_uuid', description='UUID da Despesa', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        description="Retorna lista de despesas por filtro aplicado."
    )
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
                'mensagem': ('É necessário enviar a o número do documento '
                             'como parâmetro. Ex: cpf_cnpj_fornecedor=455..')
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        associacao__uuid = request.query_params.get('associacao__uuid')
        if associacao__uuid is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': ('É necessário enviar a o uuid da '
                             'associação como parâmetro. Ex: associacao__uuid=GSDHH3434..')
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

    @action(detail=False, url_path='tags-informacoes',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def tags_informacoes_list(self, request):

        result = Despesa.get_tags_informacoes_list()

        return Response(result)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='data', description='Data', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='associacao_uuid', description='UUID da Associação', required=True,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: OpenApiResponse(
            response={
                'type': 'object',
                'properties': {
                    'erro_data_da_despesa': {'type': 'string'},
                    'data_de_encerramento': {'type': 'string'},
                    'mensagem': {'type': 'string'},
                    'status': {'type': 'integer'},
                },
            }
        )},
        description="Valida data de despesa."
    )
    @action(detail=False, url_path='validar-data-da-despesa', methods=['get'],
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def valida_data_da_despesa(self, request):
        from ..serializers.validation_serializers.despesas_validate_serializer import \
            ValidarDataDespesaValidationSerializer

        from ...services.valida_data_despesa_service import ValidaDataDaDespesaAssociacaoEncerrada

        query = ValidarDataDespesaValidationSerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)

        associacao_uuid = request.query_params.get('associacao_uuid')
        associacao = Associacao.by_uuid(associacao_uuid)

        data_da_despesa = request.query_params.get('data')
        data_da_despesa = datetime.datetime.strptime(data_da_despesa, '%Y-%m-%d')
        data_da_despesa = data_da_despesa.date()

        response = ValidaDataDaDespesaAssociacaoEncerrada(data_da_despesa=data_da_despesa,
                                                          associacao=associacao).response

        status_response = response.pop("status")

        return Response(response, status=status_response)
