"""
Módulo de API para gerenciamento da priotidades do Plano Anual de Atividades (PAA).

Este módulo concentra os endpoints de listagem, consulta, criação, atualização,
exclusão em lote as prioridades de PAA, duplicação uma PrioridadePaa existente,
retornar a tabela com informações vinculada ao PAA e remoção de prioridades.
Também listar e recuperar prioridades do PAA para o relatório.
"""
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import NotFound
from django.http import Http404
import logging
import django_filters
from waffle.mixins import WaffleFlagMixin
from django.db.models import QuerySet

from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.paa.models import PrioridadePaa, Paa
from sme_ptrf_apps.paa.models.prioridade_paa import SimNaoChoices
from sme_ptrf_apps.paa.api.serializers import (
    PrioridadePaaCreateUpdateSerializer,
    PrioridadePaaListSerializer
)
from rest_framework.serializers import Serializer
from sme_ptrf_apps.paa.services import RetificacaoPaaService
from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoAPITodosComGravacao
from sme_ptrf_apps.paa.querysets import queryset_prioridades_paa
from drf_spectacular.utils import extend_schema_view
from sme_ptrf_apps.paa.api.views.docs.prioridade_paa_docs import DOCS
from sme_ptrf_apps.paa.api.views.docs.prioridade_paa_relatorio_docs import DOCS as DOCS_RELATORIO

from sme_ptrf_apps.paa.mixins.paa_bloqueia_alteracao_mixin import PaaBloqueiaAlteracaoMixin
from sme_ptrf_apps.paa.services.paa_status_bloqueia_alteracao_service import (
    PaaStatusBloqueiaAlteracaoService,
    TipoBloqueioPaa
)

logger = logging.getLogger(__name__)


@extend_schema_view(**DOCS)
class PrioridadePaaViewSet(WaffleFlagMixin, PaaBloqueiaAlteracaoMixin, ModelViewSet):
    """
    ViewSet responsável pelo gerenciamento das prioridades do PAA.

    Disponibiliza operações de listagem, consulta, criação, atualização
    e remoção de prioridades, permitindo a filtragem por PAA, ação da
    associação, programa PDDE, ação PDDE, recurso, tipo de aplicação,
    tipo de despesa de custeio, especificação de material e indicador
    de prioridade.
    """
    waffle_flag = "paa"
    tipo_bloqueio_paa = TipoBloqueioPaa.STATUS_GERADO
    permission_classes = [PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = PrioridadePaa.objects.all()
    serializer_class = PrioridadePaaCreateUpdateSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    pagination_class = CustomPagination
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = (
        'acao_associacao__uuid',
        'paa__uuid',
        'recurso',
        'prioridade',  # 0 (False) ou 1 (True)
        'programa_pdde__uuid',
        'acao_pdde__uuid',
        'tipo_aplicacao',
        'tipo_despesa_custeio__uuid',
        'especificacao_material__uuid',
    )

    def get_queryset(self) -> QuerySet:
        """
        Retorne a queryset de prioridades PAA.

        Returns:
            QuerySet: Queryset de prioridades PAA filtrada.
        """
        qs = super().get_queryset()
        qs = queryset_prioridades_paa(qs)

        return qs

    def get_serializer_class(self) -> type[Serializer]:
        """
        Retorne o serializer apropriado para a ação executada.

        Utiliza o serializer de listagem para as operações de listar e
        o serializer createupdate padrão para as demais ações.

        Returns:
            Serializer: Classe do serializer correspondente à ação atual.
        """
        if self.action == 'list':
            return PrioridadePaaListSerializer
        else:
            return PrioridadePaaCreateUpdateSerializer

    @action(detail=False, methods=['get'], url_path='tabelas',
            permission_classes=[PermissaoApiUe])
    def tabelas(self, request: Request, *args, **kwrgs) -> Response:
        """
        Retorne a tabela com informações vinculada ao PAA.

        Params:
            paa__uuid: uuid do paa

        Return:
            Retorna a tabela com informações vinculada ao PAA.
        """
        from sme_ptrf_apps.paa.services import AcoesPaaService
        paa_uuid = request.query_params.get('paa__uuid')

        try:
            paa = Paa.by_uuid(paa_uuid)
        except Paa.DoesNotExist:
            raise serializers.ValidationError({"non_field_errors": "PAA não identificado."})

        outros_recursos = AcoesPaaService(paa).obter_outros_recursos_periodo()
        outros_recursos = [
            {
                "uuid": outro_recurso_periodo.outro_recurso.uuid,
                "nome": outro_recurso_periodo.outro_recurso.nome
            } for outro_recurso_periodo in outros_recursos]

        tabelas = {
            'prioridades': SimNaoChoices.to_dict(),
            'recursos': RecursoOpcoesEnum.to_dict(),
            'tipos_aplicacao': TipoAplicacaoOpcoesEnum.to_dict(),
            'outros_recursos': outros_recursos
        }

        return Response(tabelas, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='excluir-lote',
            permission_classes=[PermissaoApiUe & PermissaoAPITodosComGravacao])
    def excluir_em_lote(self, request: Request, *args, **kwargs) -> Response:
        """
        Exclua em lote as prioridades de PAA.

        Essa action pode ser usada para excluir em lote as prioridades de PAA.

        - lista_uuids: lista de uuids das prioridades a serem excluídas.

        Retorna um dicionário com as informações dos erros e a mensagem
        de sucesso ou erro.
        """
        lista_uuids = request.data.get('lista_uuids', [])

        if not len(lista_uuids):
            content = {
                'erro': 'Falta de informações',
                'mensagem': 'É necessário enviar a lista de uuids a serem excluídos (lista_uuids).'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            from sme_ptrf_apps.paa.utils import validar_lista_uuids
            validar_lista_uuids(lista_uuids)

        except Exception as err:
            return Response({
                'erro': "Falha ao excluir Prioridades em lote",
                'mensagem': str(err)
            }, status=status.HTTP_400_BAD_REQUEST)

        prioridades = PrioridadePaa.objects.filter(
            uuid__in=lista_uuids
        ).select_related("paa")

        paas = {p.paa for p in prioridades}

        PaaStatusBloqueiaAlteracaoService.validar_lista(
            paas,
            tipo_bloqueio=TipoBloqueioPaa.STATUS_GERADO,
        )

        try:
            erros = PrioridadePaa.excluir_em_lote(lista_uuids)
            if len(erros):
                mensagem = 'Alguma das prioridades selecionadas já foi removida.'
            else:
                mensagem = 'Prioridades removidas com sucesso.'
            return Response({
                'erros': erros,
                'mensagem': mensagem
            }, status=status.HTTP_200_OK)

        except Exception as err:
            error = {
                'erro': "Falha ao excluir Prioridades em lote",
                'mensagem': str(err)
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """
        Atualize uma PrioridadePaa existente.

        Cenário de exceção: quando tentar atualizar uma prioridade que já foi removida.

        Valida os dados através do serializer e aplica a validação de valor.
        Retorna os dados da prioridade atualizada ou erros de validação.
        """
        try:
            self.get_object()
            return super().update(request, *args, **kwargs)

        except (Http404, NotFound):
            return Response(
                {"mensagem": "Prioridade não encontrada ou já foi removida da base de dados."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='duplicar')
    def duplicar(self, request: Request, uuid: str | None = None) -> Response:
        """
        Duplique uma PrioridadePaa existente, criando um novo registro com os mesmos dados.
        O campo `valor_total` não informado.
        """
        try:
            original = self.get_object()
        except (Http404, NotFound):
            return Response(
                {"mensagem": "Prioridade não encontrada ou já foi removida da base de dados."},
                status=status.HTTP_404_NOT_FOUND
            )

        self.validar_paa_permite_alteracao()

        original_data = {
            'paa': str(original.paa.uuid) if original.paa else None,
            'prioridade': int(original.prioridade),
            'recurso': original.recurso,
            'outro_recurso': str(original.outro_recurso.uuid) if original.outro_recurso else None,
            'acao_associacao': str(original.acao_associacao.uuid) if original.acao_associacao else None,
            'programa_pdde': str(original.programa_pdde.uuid) if original.programa_pdde else None,
            'acao_pdde': str(original.acao_pdde.uuid) if original.acao_pdde else None,
            'tipo_aplicacao': original.tipo_aplicacao,
            'tipo_despesa_custeio': str(original.tipo_despesa_custeio.uuid) if original.tipo_despesa_custeio else None,
            'especificacao_material': (
                str(original.especificacao_material.uuid) if original.especificacao_material else None),
            'valor_total': None,
            'copia_de': str(original.uuid),
        }
        original_data = {k: v for k, v in original_data.items() if v is not None}

        serializer = PrioridadePaaCreateUpdateSerializer(data=original_data)

        serializer.is_valid(raise_exception=True)
        nova_prioridade = serializer.save()

        return Response(PrioridadePaaCreateUpdateSerializer(nova_prioridade).data, status=status.HTTP_201_CREATED)


@extend_schema_view(**DOCS_RELATORIO)
class PrioridadePaaRelatorioViewSet(WaffleFlagMixin, ModelViewSet):
    """
    ViewSet responsável pela consulta de prioridades do PAA para relatórios.

    Expõe um endpoint somente leitura para listar e recuperar prioridades do
    PAA, permitindo filtragem por associação, PAA, recurso, prioridade,
    programa PDDE, ação PDDE, tipo de aplicação, tipo de despesa, especificação
    de material e outros recursos. A paginação é desabilitada para atender às
    necessidades da geração de relatórios.
    """
    waffle_flag = "paa"
    permission_classes = [PermissaoApiUe]
    lookup_field = "uuid"
    queryset = PrioridadePaa.objects.all()
    serializer_class = PrioridadePaaListSerializer
    http_method_names = ["get"]
    pagination_class = None
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = (
        "acao_associacao__uuid",
        "paa__uuid",
        "recurso",
        "prioridade",
        "programa_pdde__uuid",
        "acao_pdde__uuid",
        "tipo_aplicacao",
        "tipo_despesa_custeio__uuid",
        "especificacao_material__uuid",
        "outro_recurso__uuid",
    )

    def get_queryset(self) -> QuerySet:
        """
        Retorne a queryset de prioridades PAA.

        Returns:
            QuerySet: Queryset de prioridades PAA filtrada.
        """
        qs = super().get_queryset()
        return queryset_prioridades_paa(qs)

    def get_serializer_context(self) -> type[Serializer]:
        """
        Retorna o contexto utilizado pelo serializer.

        Adiciona ao contexto a chave ``alteracoes`` quando o parâmetro
        ``paa__uuid`` é informado na requisição e o PAA correspondente é
        encontrado. Caso o PAA não exista, apenas registra um aviso no log e
        retorna o contexto padrão.

        Returns:
            dict: Contexto utilizado pelo serializer.
        """
        context = super().get_serializer_context()
        paa_uuid = self.request.query_params.get('paa__uuid')
        if paa_uuid:
            try:
                paa = Paa.by_uuid(paa_uuid)
                context['alteracoes'] = RetificacaoPaaService(
                    paa=paa, usuario=self.request.user
                ).identificar_alteracoes()
            except Paa.DoesNotExist:
                logger.warning('PAA com uuid %s não encontrado para o relatório de prioridades', paa_uuid)
        return context

    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        Retorna a listagem das prioridades.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        data = serializer.data
        return Response(
            {
                "count": len(data),
                "results": data,
            },
            status=status.HTTP_200_OK,
        )
