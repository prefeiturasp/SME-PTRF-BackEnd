from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import django_filters
from waffle.mixins import WaffleFlagMixin
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.paa.models import OutroRecursoPeriodoPaa
from sme_ptrf_apps.paa.api.serializers import OutrosRecursosPeriodoPaaSerializer
from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoApiSME
from sme_ptrf_apps.paa.services import (
    OutroRecursoPeriodoPaaImportacaoService,
    OutroRecursoPeriodoPaaVinculoUnidadeService,
    OutroRecursoPeriodoDesabilitacaoService,
    ImportacaoUnidadesOutroRecursoException,
    UnidadeNaoEncontradaException,
    ValidacaoVinculoException,
    ConfirmacaoVinculoException,
    DesabilitacaoRecursoException,
)

from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from sme_ptrf_apps.core.api.serializers import UnidadeLookUpSerializer
import logging

logger = logging.getLogger(__name__)


class OutroRecursoPeriodoPaaFiltro(django_filters.FilterSet):
    periodo_paa_uuid = django_filters.CharFilter(lookup_expr='exact', field_name='periodo_paa__uuid')
    outro_recurso_uuid = django_filters.CharFilter(lookup_expr='exact', field_name='outro_recurso__uuid')
    outro_recurso_nome = django_filters.CharFilter(lookup_expr='icontains', field_name='outro_recurso__nome')
    ativo = django_filters.BooleanFilter(lookup_expr='exact')

    class Meta:
        model = OutroRecursoPeriodoPaa
        fields = ['periodo_paa_uuid', 'outro_recurso_uuid']


class OutrosRecursosPeriodoPaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = OutroRecursoPeriodoPaa.objects.select_related('periodo_paa', 'outro_recurso').all()
    serializer_class = OutrosRecursosPeriodoPaaSerializer
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = OutroRecursoPeriodoPaaFiltro

    @action(
        detail=True,
        methods=['post'],
        url_path='importar-unidades',
        permission_classes=[IsAuthenticated & PermissaoApiSME]
    )
    def importar_unidades(self, request, uuid=None):
        try:
            OutroRecursoPeriodoPaaImportacaoService.importar_unidades(
                destino=self.get_object(),
                origem_uuid=request.data.get('origem_uuid')
            )
        except ImportacaoUnidadesOutroRecursoException as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'detail': 'Unidades importadas com sucesso.'},
            status=status.HTTP_200_OK
        )

    def _get_service_vinculo_unidade(self) -> OutroRecursoPeriodoPaaVinculoUnidadeService:
        """
        Retorna uma instância do service para o objeto atual.

        Returns:
            Instância configurada do service
        """
        instance = self.get_object()
        return OutroRecursoPeriodoPaaVinculoUnidadeService(instance)

    def _get_service_desabilitacao(self) -> OutroRecursoPeriodoDesabilitacaoService:
        """
        Retorna uma instância do service de desabilitação para o objeto atual.
        """
        instance = self.get_object()
        return OutroRecursoPeriodoDesabilitacaoService(instance)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='dre', description='UUID da DRE', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='tipo_unidade', description='Tipo da Unidade', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='nome_ou_codigo', description='Nome da Unidade ou Código EOL', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: UnidadeLookUpSerializer()},
    )
    @action(detail=True, url_path='unidades-vinculadas',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def unidades_vinculadas(self, request, *args, **kwargs):
        uuid_dre = self.request.query_params.get('dre')
        nome_ou_codigo = self.request.query_params.get('nome_ou_codigo')
        tipo_unidade = self.request.query_params.get('tipo_unidade')

        instance = self.get_object()
        unidades_qs = instance.unidades.all()

        if uuid_dre:
            unidades_qs = unidades_qs.filter(dre__uuid=uuid_dre)

        if tipo_unidade:
            unidades_qs = unidades_qs.filter(tipo_unidade=tipo_unidade)

        if nome_ou_codigo:
            unidades_qs = unidades_qs.filter(
                Q(codigo_eol=nome_ou_codigo) | Q(nome__unaccent__icontains=nome_ou_codigo))

        serializer = UnidadeLookUpSerializer(unidades_qs, many=True)

        paginator = CustomPagination()
        paginated_unidades = paginator.paginate_queryset(serializer.data, request)

        return paginator.get_paginated_response(paginated_unidades)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='dre', description='UUID da DRE', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='nome_ou_codigo', description='Nome da Unidade ou Código EOL', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='nome_ou_codigo', description='Nome da Unidade ou Código EOL', required=False,
                             type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses={200: UnidadeLookUpSerializer()},
    )
    @action(detail=True, url_path='unidades-nao-vinculadas',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def unidades_nao_vinculadas(self, request, *args, **kwargs):
        from sme_ptrf_apps.core.models.unidade import Unidade
        uuid_dre = self.request.query_params.get('dre')
        nome_ou_codigo = self.request.query_params.get('nome_ou_codigo')
        tipo_unidade = self.request.query_params.get('tipo_unidade')

        instance = self.get_object()

        todas_unidades = Unidade.objects.select_related('dre', 'dre__dre').all()
        unidades_nao_vinculadas = todas_unidades.exclude(uuid__in=instance.unidades.values_list('uuid', flat=True))

        if uuid_dre:
            unidades_nao_vinculadas = unidades_nao_vinculadas.filter(dre__uuid=uuid_dre)

        if tipo_unidade:
            unidades_nao_vinculadas = unidades_nao_vinculadas.filter(tipo_unidade=tipo_unidade)

        if nome_ou_codigo:
            unidades_nao_vinculadas = unidades_nao_vinculadas.filter(
                Q(codigo_eol=nome_ou_codigo) | Q(nome__unaccent__icontains=nome_ou_codigo))

        serializer = UnidadeLookUpSerializer(unidades_nao_vinculadas, many=True)

        paginator = CustomPagination()
        paginated_unidades = paginator.paginate_queryset(serializer.data, request)

        return paginator.get_paginated_response(paginated_unidades)

    @extend_schema(
        responses={
            200: {
                'mensagem': {'type': 'string'},
            },
            400: {'description': 'Validação falhou'},
            404: {'description': 'Unidade não encontrada ou não vinculada'}
        }
    )
    @action(detail=True, methods=['POST'], url_path='unidade/(?P<unidade_uuid>[^/.]+)/desvincular',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def desvincular_unidade(self, request, unidade_uuid, *args, **kwargs):
        """Desvincula uma unidade do recurso período."""
        service = self._get_service_vinculo_unidade()
        confirmado = request.data.get('confirmado', False)
        try:
            if not confirmado:
                try:
                    service.validar_confirmacao_para_desvinculo_unidades([unidade_uuid])
                except ConfirmacaoVinculoException as e:
                    logger.warning(f"Validação requer confirmação ao desvincular individual: {str(e)}")
                    return Response({"confirmar": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            resultado = service.desvincular_unidades([unidade_uuid])
            return Response(resultado, status=status.HTTP_200_OK)

        except UnidadeNaoEncontradaException as e:
            logger.error(str(e), exc_info=True)
            return Response({"mensagem": str(e)}, status=status.HTTP_404_NOT_FOUND)

        except ValidacaoVinculoException as e:
            logger.error(str(e), exc_info=True)
            return Response({"mensagem": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            msg_erro = f"Erro inesperado ao desvincular unidade: {unidade_uuid}. {str(e)}"
            logger.error(msg_erro, exc_info=True)
            return Response({"mensagem": msg_erro}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'unidade_uuids': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'uuid'}
                    }
                },
                'required': ['unidade_uuids']
            }
        },
        responses={
            200: {
                'mensagem': {'type': 'string'},
            },
            400: {'description': 'Validação falhou'},
            404: {'description': 'Nenhuma unidade encontrada'}
        }
    )
    @action(detail=True, methods=['POST'], url_path='desvincular-em-lote',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def desvincular_em_lote(self, request, *args, **kwargs):
        """Desvincula múltiplas unidades do período em lote."""
        service = self._get_service_vinculo_unidade()
        unidade_uuids = request.data.get('unidade_uuids', [])
        confirmado = request.data.get('confirmado', False)

        try:
            if not confirmado:
                try:
                    service.validar_confirmacao_para_desvinculo_unidades(unidade_uuids)
                except ConfirmacaoVinculoException as e:
                    logger.warning(f"Validação requer confirmação ao desvincular em lote: {str(e)}")
                    return Response({"confirmar": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            resultado = service.desvincular_unidades(unidade_uuids)
            return Response(resultado, status=status.HTTP_200_OK)

        except UnidadeNaoEncontradaException as e:
            logger.error(str(e), exc_info=True)
            return Response({"mensagem": str(e)}, status=status.HTTP_404_NOT_FOUND)

        except ValidacaoVinculoException as e:
            logger.error(str(e), exc_info=True)
            return Response({"mensagem": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            msg_erro = "Erro ao desvincular em lote"
            logger.error(f'{msg_erro} - {str(e)}', exc_info=True)
            return Response({"mensagem": msg_erro}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'unidade_uuids': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'uuid'}
                    }
                },
                'required': ['unidade_uuids']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'mensagem': {'type': 'string'},
                    'total_desvinculado': {'type': 'integer'},
                    'unidades_desvinculadas': {'type': 'array', 'items': {'type': 'string'}}
                }
            },
            400: {'description': 'Validação falhou'},
            404: {'description': 'Nenhuma unidade encontrada'}
        }
    )
    @action(detail=True, methods=['POST'], url_path='vincular-todas-unidades',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def vincular_todas_unidades(self, request, *args, **kwargs):
        """Habilita o recurso para todas as unidades."""
        service = self._get_service_vinculo_unidade()

        try:
            resultado = service.vincular_todas_unidades()
            return Response(resultado, status=status.HTTP_200_OK)
        except Exception as e:
            msg_erro = "Erro ao vincular todas as unidades."
            logger.error(f"{msg_erro} {str(e)}", exc_info=True)
            return Response({"mensagem": msg_erro}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            200: {
                'mensagem': {'type': 'string'},
            },
            400: {'description': 'Validação falhou'},
            404: {'description': 'Unidade não encontrada'}
        }
    )
    @action(detail=True, methods=['POST'], url_path='unidade/(?P<unidade_uuid>[^/.]+)/vincular',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def vincular_unidade(self, request, unidade_uuid, *args, **kwargs):
        """Vincula uma unidade ao recurso do período."""
        service = self._get_service_vinculo_unidade()
        confirmado = request.data.get('confirmado', False)

        try:
            if not confirmado:
                try:
                    service.validar_confirmacao_para_vinculo_unidades([unidade_uuid])
                except ConfirmacaoVinculoException as e:
                    logger.warning(f"Validação requer confirmação ao vincular individual: {str(e)}")
                    return Response({"confirmar": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            resultado = service.vincular_unidades([unidade_uuid])
            return Response(resultado, status=status.HTTP_200_OK)

        except UnidadeNaoEncontradaException as e:
            logger.error(f"{str(e)}", exc_info=True)
            return Response({"mensagem": str(e)}, status=status.HTTP_404_NOT_FOUND)

        except ValidacaoVinculoException as e:
            msg_erro = f"Validação falhou ao vincular: {str(e)}"
            logger.error(msg_erro, exc_info=True)
            return Response({"mensagem": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            msg_erro = "Erro ao vincular unidade."
            logger.error(f"{msg_erro}. {str(e)}", exc_info=True)
            return Response({"mensagem": msg_erro}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'unidade_uuids': {
                        'type': 'array',
                        'items': {'type': 'string', 'format': 'uuid'}
                    }
                },
                'required': ['unidade_uuids']
            }
        },
        responses={
            200: {
                'mensagem': {'type': 'string'},
            },
            400: {'description': 'Validação falhou'},
            404: {'description': 'Nenhuma unidade encontrada'}
        }
    )
    @action(detail=True, methods=['POST'], url_path='vincular-em-lote',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def vincular_em_lote(self, request, *args, **kwargs):
        """Vincula múltiplas unidades ao recurso do período em lote."""
        service = self._get_service_vinculo_unidade()
        unidade_uuids = request.data.get('unidade_uuids', [])
        confirmado = request.data.get('confirmado', False)

        try:
            if not confirmado:
                try:
                    service.validar_confirmacao_para_vinculo_unidades(unidade_uuids)
                except ConfirmacaoVinculoException as e:
                    logger.warning(f"Validação requer confirmação ao vincular em lote: {str(e)}")
                    return Response({"confirmar": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            resultado = service.vincular_unidades(unidade_uuids)
            return Response(resultado, status=status.HTTP_200_OK)

        except UnidadeNaoEncontradaException as e:
            logger.error(f"Nenhuma unidade encontrada no lote. {str(e)}", exc_info=True)
            return Response({"mensagem": str(e)}, status=status.HTTP_404_NOT_FOUND)

        except ValidacaoVinculoException as e:
            logger.warning(f"Validação ao vincular lote: {str(e)}")
            return Response({"mensagem": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            msg_erro = f'Falha ao vincular em lote: {str(e)}'
            logger.error(msg_erro, exc_info=True)
            return Response({"mensagem": msg_erro}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'recurso': {'type': 'string'},
                    'periodo': {'type': 'string'},
                    'total_paas': {'type': 'integer'},
                    'paas_em_elaboracao': {'type': 'integer'},
                    'paas_gerados_ou_retificacao': {'type': 'integer'},
                    'detalhes': {
                        'type': 'object',
                        'properties': {
                            'em_elaboracao': {'type': 'array'},
                            'gerados_ou_retificacao': {'type': 'array'}
                        }
                    }
                }
            },
            404: {'description': 'Recurso não encontrado'}
        }
    )
    @action(
        detail=True,
        methods=['GET'],
        url_path='informacoes-desabilitacao',
        permission_classes=[IsAuthenticated & PermissaoApiUe]
    )
    def informacoes_desabilitacao(self, request, uuid=None):
        """
        Obtém informações sobre os impactos da desabilitação do recurso.
        Usado para exibir na modal de confirmação.
        """
        try:
            service = self._get_service_desabilitacao()
            informacoes = service.obter_informacoes_para_confirmacao()

            return Response(informacoes, status=status.HTTP_200_OK)

        except Exception as e:
            msg_error = f"Erro ao obter informações de desabilitação: {str(e)}"
            logger.error(msg_error, exc_info=True)
            return Response({'mensagem': msg_error}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'sucesso': {'type': 'boolean'},
                    'mensagem': {'type': 'string'},
                    'recurso': {'type': 'string'},
                    'periodo': {'type': 'string'},
                    'total_paas': {'type': 'integer'},
                    'paas_processados': {'type': 'array'}
                }
            },
            400: {'description': 'Erro ao desabilitar recurso'},
            404: {'description': 'Recurso não encontrado'}
        }
    )
    @action(
        detail=True,
        methods=['PATCH'],
        url_path='desabilitar',
        permission_classes=[IsAuthenticated & PermissaoApiUe]
    )
    def desabilitar(self, request, uuid=None):
        """
        Desabilita o recurso aplicando as regras de negócio conforme o status dos PAAs.

        Status do PAA:
        - Em elaboração: remove o recurso de Receitas Previstas e Prioridades
        - Gerado/Em retificação: mantém o recurso em Receitas Previstas e Prioridades
        """
        try:
            instance = self.get_object()

            if not instance.ativo:
                return Response({'mensagem': 'O recurso já está desabilitado.'}, status=status.HTTP_400_BAD_REQUEST)

            service = self._get_service_desabilitacao()
            resultado = service.desabilitar_outro_recurso_periodo()

            return Response(resultado, status=status.HTTP_200_OK)

        except DesabilitacaoRecursoException as e:
            logger.error(f"Erro ao desabilitar recurso: {str(e)}", exc_info=True)
            return Response({'mensagem': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Erro inesperado ao desabilitar recurso: {str(e)}", exc_info=True)
            return Response(
                {'mensagem': 'Erro ao desabilitar outro recurso.'},
                status=status.HTTP_400_BAD_REQUEST
            )
