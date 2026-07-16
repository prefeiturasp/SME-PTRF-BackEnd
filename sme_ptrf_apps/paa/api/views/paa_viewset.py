"""
Módulo de API para gerenciamento do Plano Anual de Atividades (PAA).

Este módulo concentra os endpoints e regras de negócio para criação,
atualização, exclusão, geração de relatórios em PDF, congelamento de saldos,
e fluxos de retificação do PAA.
"""
import logging
from datetime import datetime
from time import sleep
from django.http import HttpResponse
from django.http import Http404
from django.db.models import Q
from django.db import models
from django.db.models.functions import Lower
from django.db.models import QuerySet
from rest_framework.serializers import Serializer

from waffle.mixins import WaffleFlagMixin
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import (
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoApiUe
)
from sme_ptrf_apps.paa.api.serializers.paa_serializer import (
    PaaSerializer,
    PaaUpdateSerializer,
    PaaRetificacaoComparativoSerializer,
)
from sme_ptrf_apps.paa.api.serializers.renderizador_paa_serializer import RenderizadorPaaBuilder
from sme_ptrf_apps.paa.api.serializers.receita_prevista_paa_serializer import ReceitaPrevistaPaaSerializer
from sme_ptrf_apps.logging.loggers import ContextualLogger
from sme_ptrf_apps.paa.models import Paa, PeriodoPaa
from sme_ptrf_apps.paa.models.documento_paa import DocumentoPaa, obter_documento_final_por_retificacao
from sme_ptrf_apps.paa.services.documento_paa_service import DocumentoPaaService
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa.services.paa_service import PaaService, ImportacaoConfirmacaoNecessaria
from sme_ptrf_apps.paa.services.receitas_previstas_paa_service import SaldosPorAcaoPaaService
from sme_ptrf_apps.paa.services.resumo_prioridades_service import ResumoPrioridadesService
from sme_ptrf_apps.paa.services.acoes_paa_service import AcoesReceitasPrevistasPaaService
from sme_ptrf_apps.paa.services.valida_geracao_documentos_service import (
    ValidaGeracaoDocumentoPAAService)

from sme_ptrf_apps.paa.tasks.gerar_documento_paa import gerar_documento_paa_async
from sme_ptrf_apps.paa.tasks.gerar_previa_documento_paa import gerar_previa_documento_paa_async
from sme_ptrf_apps.paa.tasks.gerar_documento_paa_retificacao import gerar_documento_paa_retificacao_async
from sme_ptrf_apps.paa.tasks.gerar_previa_documento_paa_retificacao import gerar_previa_documento_paa_retificacao_async
from sme_ptrf_apps.paa.services.retificacao_paa_service import (
    RetificacaoPaaService,
    ValidacaoRetificacao,
)
from sme_ptrf_apps.paa.services.cancela_retificacao_paa_service import (
    CancelaRetificacaoPaaService,
    ValidacaoCancelaRetificacao,
)
from drf_spectacular.utils import extend_schema_view
from .docs.paa_viewset_docs import DOCS as PAA_DOCS

from sme_ptrf_apps.paa.mixins.paa_bloqueia_alteracao_mixin import PaaBloqueiaAlteracaoMixin
from sme_ptrf_apps.paa.services.paa_status_bloqueia_alteracao_service import TipoBloqueioPaa

logger = logging.getLogger(__name__)


@extend_schema_view(**PAA_DOCS)
class PaaViewSet(WaffleFlagMixin, PaaBloqueiaAlteracaoMixin, ModelViewSet):
    """
    ViewSet responsável pelo gerenciamento do PAA.

    Disponibiliza rotas e ações customizadas para o ciclo de vida do
    Plano Anual de Atividades, gerenciado por permissões escolares e flags.
    """

    waffle_flag = "paa"
    tipo_bloqueio_paa = TipoBloqueioPaa.STATUS_GERADO
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Paa.objects.all()
    serializer_class = PaaSerializer
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_serializer_class(self) -> type[Serializer]:
        """
        Retorne a classe de serializer com base na ação atual da viewset.

        Returns:
            A classe do serializer correspondente à requisição.
        """
        if self.action == 'partial_update':
            return PaaUpdateSerializer
        else:
            return PaaSerializer

    def get_queryset(self) -> QuerySet:
        """
        Retorne a lista de PAAs filtrada pelos parâmetros da requisição.

        Filtra os registros por uma associação específica se o parâmetro
        'associacao_uuid' for fornecido na URL.

        Returns:
            O queryset contendo os registros de PAA filtrados.
        """
        qs = self.queryset
        associacao = self.request.query_params.get('associacao_uuid', None)

        if associacao is not None:
            qs = qs.filter(associacao__uuid=associacao)

        return qs

    @action(detail=False, methods=['get'], url_path='download-pdf-levantamento-prioridades',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def download_levantamento_prioridades_paa(self, request: Request) -> Response:
        """
        Gere e faça o download do PDF de levantamento de prioridades do PAA.

        Args:
            request: O objeto de requisição HTTP atual.

        Returns:
            Uma resposta HTTP contendo o payload do arquivo PDF gerado.
        """
        associacao_uuid = self.request.query_params.get('associacao_uuid')
        associacao = Associacao.objects.filter(uuid=associacao_uuid).first()
        if associacao:
            nome_unidade = associacao.unidade.nome
            tipo_unidade = associacao.unidade.tipo_unidade
            associacao_nome = associacao.nome
        else:
            nome_unidade = None
            tipo_unidade = None
            associacao_nome = None

        dados = {
            "nome_associacao": associacao_nome,
            "nome_unidade": nome_unidade,
            "tipo_unidade": tipo_unidade,
            "username": request.user.username,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "ano": datetime.now().year,
            "rodape": (
                f"Unidade Educacional: {tipo_unidade} {nome_unidade}. "
                f"Documento gerado pelo usuário: {request.user.username}, "
                f"via SIG - Escola, em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
        }
        return PaaService.gerar_arquivo_pdf_levantamento_prioridades_paa(dados)

    @action(detail=True, methods=['post'], url_path='desativar-atualizacao-saldo',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def desativar_atualizacao_saldo(self, request: Request, uuid: str) -> Response:
        """
        Congele os saldos atuais por ação vinculados a este PAA.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Uma resposta contendo as receitas previstas com saldos congelados.
        """
        instance = self.get_object()
        associacao = instance.associacao

        saldos_por_acao_paa_service = SaldosPorAcaoPaaService(paa=instance, associacao=associacao)
        try:
            receitas_previstas = saldos_por_acao_paa_service.congelar_saldos()
        except Exception as e:
            logger.exception(f'Erro ao congelar saldos do PAA {instance.uuid}: {e}')
            return Response(
                {'mensagem': f'{e}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReceitaPrevistaPaaSerializer(receitas_previstas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='ativar-atualizacao-saldo',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def ativar_atualizacao_saldo(self, request: Request, uuid: str) -> Response:
        """
        Impeça o descongelamento caso o documento final do PAA já tenha sido
        concluído e gerado.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Uma resposta contendo as receitas previstas atualizadas.
        """
        instance = self.get_object()

        # Bloqueia descongelar saldos quando o documento final foi gerado
        documento_final = instance.documento_final
        if documento_final and documento_final.concluido:
            return Response(
                {'mensagem': 'Não é possível descongelar saldos após a geração do documento final do PAA.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        associacao = instance.associacao

        saldos_por_acao_paa_service = SaldosPorAcaoPaaService(paa=instance, associacao=associacao)
        receitas_previstas = saldos_por_acao_paa_service.descongelar_saldos()

        serializer = ReceitaPrevistaPaaSerializer(receitas_previstas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Exclua um registro de PAA caso não possua restrições de integridade.

        Args:
            request: O objeto de requisição HTTP atual.
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            Uma resposta indicando remoção bem-sucedida ou erro de proteção.
        """
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Este PAA não pode ser excluído porque já está sendo usado na aplicação.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='resumo-prioridades',
            permission_classes=[PermissaoApiUe])
    def resumo_prioridades(self, request: Request, uuid: str | None = None) -> Response:
        """
        Retorne o resumo das prioridades definidas para o PAA atual.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Uma resposta contendo o agrupamento estruturado do resumo.
        """
        result = ResumoPrioridadesService(self.get_object()).resumo_prioridades()
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='paas-anteriores',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def paa_anteriores(self, request: Request, uuid: str | None = None) -> Response:
        """
        Retorne a lista de relatórios de PAAs anteriores da mesma associação.

        Filtra os registros por períodos cuja data inicial seja inferior ao
        período do PAA referenciado.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA de referência.

        Returns:
            Uma lista de registros históricos de PAA serializados.
        """
        paa_atual = self.get_object()
        paas_anteriores = self.queryset.filter(
            periodo_paa__data_inicial__lt=paa_atual.periodo_paa.data_inicial,
            associacao=paa_atual.associacao
        ).order_by('-periodo_paa__data_inicial')

        serializer = PaaSerializer(paas_anteriores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='paa-vigente-e-anteriores',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def paa_vigente_e_anteriores(self, request: Request) -> Response:
        """
        Retorne o PAA vigente e o histórico dos anteriores renderizados.

        Args:
            request: O objeto de requisição HTTP atual.

        Returns:
            Um dicionário contendo as estruturas renderizadas do PAA vigente e
            uma lista para os anteriores.
        """
        associacao_uuid = self.request.query_params.get('associacao_uuid')

        if not associacao_uuid:
            content = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário informar o uuid da associação.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
        except (Associacao.DoesNotExist, ValueError):
            content = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto associação para o uuid {associacao_uuid} não foi encontrado na base."
            }
            return Response(content, status=status.HTTP_404_NOT_FOUND)

        periodo_paa_vigente = PeriodoPaa.periodo_vigente()
        if not periodo_paa_vigente:
            return Response(status=status.HTTP_404_NOT_FOUND)

        paas_andamento_gerados_e_parciais = Paa.objects.filter(
            pk=models.OuterRef('id')).paas_gerados_e_parciais()

        paas_em_retificacao = Paa.objects.filter(
            pk=models.OuterRef('id')).paas_em_retificacao()

        paa_vigente = (
            self.queryset.select_related('periodo_paa', 'associacao__unidade')
            .filter(
                Q(models.Exists(paas_andamento_gerados_e_parciais) | Q(models.Exists(paas_em_retificacao))),
                periodo_paa=periodo_paa_vigente,
                associacao=associacao,
            )
            .first()
        )

        paas_anteriores = (
            self.queryset.select_related('periodo_paa', 'associacao__unidade')
            .filter(
                periodo_paa__data_inicial__lt=periodo_paa_vigente.data_inicial,
                associacao=associacao,
            )
            .paas_gerados()
            .order_by('-periodo_paa__data_inicial')
        )

        def montar_render(paa, eh_paa_vigente) -> Response:
            return RenderizadorPaaBuilder(
                paa,
                request=request,
                usuario=request.user,
            ).build(eh_paa_vigente=eh_paa_vigente)

        result = {
            'vigente': montar_render(paa_vigente, True) if paa_vigente else None,
            'anteriores': [montar_render(p, False) for p in paas_anteriores],
        }

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='importar-prioridades/(?P<uuid_paa_anterior>[a-f0-9-]+)',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def importar_prioridades(self, request: Request, uuid: str | None = None,
                             uuid_paa_anterior: str | None = None) -> Response:
        """
        Importe prioridades de PAA anterior.

        Essa action pode ser usada para importar as prioridades de PAA anterior
        para o PAA atual.

        - uuid_paa_anterior: uuid do PAA anterior para importar as prioridades.

        Retorne um dicionário com a mensagem de sucesso e a quantidade de
        prioridades importadas.
        """
        confirmar = bool(int(self.request.query_params.get('confirmar', 0)))
        try:
            paa_atual = self.get_object()
        except (Http404, NotFound, Paa.DoesNotExist):
            return Response({"mensagem": "PAA atual não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        try:
            paa_anterior = Paa.objects.get(uuid=uuid_paa_anterior)
        except (Http404, NotFound, Paa.DoesNotExist):
            return Response({"mensagem": "PAA anterior não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        self.validar_paa_permite_alteracao()  # não permite importar prioridades se gerado

        try:
            importados = PaaService.importar_prioridades_paa_anterior(paa_atual, paa_anterior, confirmar)
        except ImportacaoConfirmacaoNecessaria as e:
            return Response({"confirmar": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"mensagem": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        result = {
            'mensagem': 'Prioridades importadas com sucesso.' if len(importados) > 0 else (
                'Nenhuma prioridade encontrada para importação'),
        }

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='receitas-previstas',
            permission_classes=[IsAuthenticated])
    def receitas_previstas(self, request: Request, uuid: str | None = None) -> Response:
        """
        Retorne as ações e associações com as receitas previstas vinculadas.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Uma resposta contendo as ações e receitas populadas em formato dict.
        """
        paa = self.get_object()
        acoes_associacoes = AcoesReceitasPrevistasPaaService(paa).serialized_ptrf_com_receitas_previstas()

        return Response(acoes_associacoes, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='plano-orcamentario',
            permission_classes=[IsAuthenticated])
    def plano_orcamentario(self, request: Request, uuid: str | None = None) -> Response:
        """
        Retorne o plano orçamentário completo com dados consolidados.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Dicionário com a estrutura e somatórios do plano orçamentário.

        Raises:
            ValidationError: Caso ocorra alguma falha no processamento.
        """
        from sme_ptrf_apps.paa.services.plano_orcamentario_service import PlanoOrcamentarioService

        paa = self.get_object()

        try:
            service = PlanoOrcamentarioService(paa)
            dados = service.construir_plano_orcamentario()

            return Response(dados, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Erro ao construir plano orçamentário para PAA {paa.uuid}: {str(e)}", exc_info=True)
            raise ValidationError(f"Erro ao processar plano orçamentário: {str(e)}")

    @action(detail=True, methods=['get'], url_path='plano-aplicacao',
            permission_classes=[IsAuthenticated])
    def plano_aplicacao(self, request: Request, uuid: str | None = None) -> Response:
        """
        Retorne o plano de aplicação agrupado e estruturado para renderização direta

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Dicionário contendo os dados estruturados do plano de aplicação.

        Raises:
            ValidationError: Caso haja falhas na construção do plano de aplicação.
        """
        from sme_ptrf_apps.paa.services.plano_aplicacao_service import PlanoAplicacaoService

        paa = self.get_object()

        try:
            service = PlanoAplicacaoService(paa, usuario=request.user)
            dados = service.construir_plano_aplicacao()
            return Response(dados, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(f"Erro ao construir plano de aplicação para PAA {paa.uuid}: {str(e)}", exc_info=True)
            raise ValidationError(f"Erro ao processar plano de aplicação: {str(e)}")

    @action(detail=True, methods=['get'], url_path='objetivos',
            permission_classes=[IsAuthenticated])
    def objetivos_disponiveis(self, request: Request, uuid: str | None = None) -> Response:
        """
        Retorne a listagem de objetivos globais ou vinculados a este PAA.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Lista de objetivos ordenados por nome.
        """
        from sme_ptrf_apps.paa.api.serializers.objetivo_paa_serializer import ObjetivoPaaSerializer
        from sme_ptrf_apps.paa.models.objetivo_paa import ObjetivoPaa

        paa = self.get_object()

        objetivos = ObjetivoPaa.objects.filter(Q(paa__isnull=True) | Q(paa=paa)).order_by(Lower("nome"))

        serializer = ObjetivoPaaSerializer(objetivos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='atividades-estatutarias-disponiveis',
            permission_classes=[IsAuthenticated])
    def atividades_estatutarias_disponiveis(self, request: Request, uuid: str | None = None) -> Response:
        """
        Retorne as atividades estatutárias disponíveis marcando alterações.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Lista de atividades estatutárias mapeadas com contexto de retificação.
        """
        from sme_ptrf_apps.paa.api.serializers.atividade_estatutaria_serializer import AtividadeEstatutariaSerializer
        from sme_ptrf_apps.paa.models.atividade_estatutaria import AtividadeEstatutaria

        paa = self.get_object()
        alteracoes = RetificacaoPaaService(paa=paa, usuario=request.user).identificar_alteracoes()

        objetivos = AtividadeEstatutaria.disponiveis_ordenadas(paa)

        serializer = AtividadeEstatutariaSerializer(
            objetivos,
            many=True,
            context={'alteracoes': alteracoes},
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='atividades-estatutarias-previstas',
            permission_classes=[IsAuthenticated])
    def atividades_estatutarias_previstas(self, request: Request, uuid: str | None = None) -> Response:
        """
        Retorne as atividades estatutárias associadas e planejadas do PAA.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Lista serializada com as atividades previstas em andamento.
        """
        from sme_ptrf_apps.paa.api.serializers.atividade_estatutaria_paa_serializer import AtividadeEstatutariaPaaSerializer  # noqa

        paa = self.get_object()

        serializer = AtividadeEstatutariaPaaSerializer(paa.atividadeestatutariapaa_set.all(), many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='recursos-proprios-previstos',
            permission_classes=[IsAuthenticated])
    def recursos_proprios_previstos(self, request: Request, uuid: str | None = None) -> Response:
        """
        Retorne a relação de recursos próprios previstos mapeando alterações.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Lista de recursos próprios vinculados ao PAA com o contexto de alterações.
        """
        from sme_ptrf_apps.paa.api.serializers.recurso_proprio_paa_serializer import RecursoProprioPaaListSerializer

        paa = self.get_object()
        alteracoes = RetificacaoPaaService(paa=paa, usuario=request.user).identificar_alteracoes()

        serializer = RecursoProprioPaaListSerializer(
            paa.recursopropriopaa_set.all(),
            many=True,
            context={'alteracoes': alteracoes},
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='outros-recursos-do-periodo',
            permission_classes=[IsAuthenticated])
    def outros_recursos_periodo(self, request: Request, uuid: str | None = None) -> Response:
        """
        Retorne outros tipos de recursos financeiros mapeados no período do PAA.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Lista com os outros recursos agregados no período.
        """
        paa = self.get_object()

        data = AcoesReceitasPrevistasPaaService(paa).serialized_outros_recursos_periodo_com_receitas_previstas()

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="gerar-documento")
    def gerar_documento(self, request: Request, uuid: str | None = None) -> Response:
        """
        Dispare o processo assíncrono de geração do arquivo de documento final.

        Valida se as premissas de negócio permitem o fechamento do documento e
        se o payload contém o parâmetro 'confirmar'.

        Args:
            request: O objeto de requisição HTTP contendo o body da mensagem.
            uuid: O identificador único do PAA.

        Returns:
            Uma resposta notificando o início bem-sucedido ou erros impeditivos.
        """
        paa = self.get_object()
        usuario = request.user

        valida_pode_gerar = ValidaGeracaoDocumentoPAAService()
        try:
            valida_pode_gerar.valida_gerar_documento_final(paa)
        except Exception as e:
            return Response(
                {"mensagem": str(e), "error": "valida_gerar_documento_final"},
                status=status.HTTP_400_BAD_REQUEST)

        service = PaaService()
        errors = service.pode_gerar_documento_final(paa)

        if errors:
            return Response(
                {"mensagem": "\n".join(errors)},
                status=status.HTTP_400_BAD_REQUEST
            )

        confirmar = bool(int(self.request.data.get('confirmar', 0)))
        if not confirmar:
            return Response({"confirmar": "Geração não foi confirmada"}, status=status.HTTP_400_BAD_REQUEST)

        gerar_documento_paa_async.apply_async(
            args=[str(paa.uuid), usuario.username]
        )

        return Response(
            {"mensagem": "Geração de documento final iniciada"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="gerar-previa-documento")
    def gerar_previa_documento(self, request: Request, uuid: str | None = None) -> Response:
        """
        Inicie a geração em background da prévia do documento em PDF.

        Impede a chamada se o documento final já existir ou se houver outra
        solicitação de prévia ativamente sob processamento.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Resposta de agendamento da rotina assíncrona ou status 400.
        """
        sleep(2)  # Time sleep para não gerar paralelismo da geração da prévia com a geração do documento final.
        paa = self.get_object()
        usuario = request.user

        valida_pode_gerar = ValidaGeracaoDocumentoPAAService()
        try:
            valida_pode_gerar.valida_gerar_documento_previa(paa)
        except Exception as e:
            return Response({"mensagem": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        logger = ContextualLogger.get_logger(
            __name__,
            operacao='Plano Anual de Atividades',
            username=usuario.username,
        )
        DocumentoPaaService(paa=paa, usuario=usuario, previa=True, logger=logger).iniciar()

        gerar_previa_documento_paa_async.apply_async(
            args=[str(paa.uuid), usuario.username]
        )

        return Response(
            {"mensagem": "Geração de documento prévia iniciada"},
            status=200
        )

    @action(detail=True, methods=["post"], url_path="gerar-previa-retificacao",
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def gerar_previa_retificacao(self, request: Request, uuid: str | None = None) -> Response:
        """
        Inicie a geração em background da prévia da retificação do documento em PDF.

        Args:
            request: O objeto de requisição HTTP atual.

        Returns:
            Resposta de agendamento da rotina assíncrona ou status 400.
        """
        paa = self.get_object()
        usuario = request.user

        valida_pode_gerar = ValidaGeracaoDocumentoPAAService()
        try:
            valida_pode_gerar.valida_gerar_documento_previa_retificacao(paa, usuario)
        except Exception as e:
            return Response({"mensagem": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        logger = ContextualLogger.get_logger(
            __name__,
            operacao='Retificação - Plano Anual de Atividades',
            username=usuario.username,
        )
        DocumentoPaaService(paa=paa, usuario=usuario, previa=True, logger=logger, retificacao=True).iniciar()

        gerar_previa_documento_paa_retificacao_async.apply_async(
            args=[str(paa.uuid), usuario.username]
        )

        return Response({"mensagem": "Geração de prévia de retificação iniciada"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="gerar-documento-retificacao",
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def gerar_documento_retificacao(self, request: Request, uuid: str | None = None) -> Response:
        """
        Inicie a geração em background do documento de retificação em PDF.

        Args:
            request: O objeto de requisição HTTP atual.

        Returns:
            Resposta de agendamento da rotina assíncrona ou status 400.
        """
        paa = self.get_object()
        usuario = request.user

        valida_pode_gerar = ValidaGeracaoDocumentoPAAService()
        try:
            valida_pode_gerar.valida_gerar_documento_final_retificacao(paa, usuario)
        except Exception as e:
            return Response({"mensagem": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        service = PaaService()
        errors = service.pode_gerar_documento_final(paa)

        if errors:
            return Response(
                {"mensagem": "\n".join(errors)},
                status=status.HTTP_400_BAD_REQUEST
            )

        confirmar = bool(int(self.request.data.get('confirmar', 0)))
        if not confirmar:
            return Response({"confirmar": "Geração não foi confirmada"}, status=status.HTTP_400_BAD_REQUEST)

        logger = ContextualLogger.get_logger(
            __name__,
            operacao='Retificação - Plano Anual de Atividades',
            username=usuario.username,
        )
        DocumentoPaaService(paa=paa, usuario=usuario, previa=False, logger=logger, retificacao=True).iniciar()

        gerar_documento_paa_retificacao_async.apply_async(
            args=[str(paa.uuid), usuario.username]
        )

        return Response({"mensagem": "Geração de documento de retificação iniciada"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='documento-final',
            permission_classes=[IsAuthenticated])
    def documento_final(self, request: Request, uuid: str | None = None) -> Response:
        """
        Retorne o documento final concluído para download.

        Permite buscar arquivos históricos de retificação por parâmetro na URL.

        Args:
            request: O objeto de requisição HTTP contendo query params.
            uuid: O identificador único do PAA.

        Returns:
            Um HttpResponse transmitindo o fluxo de bytes do PDF em anexo.
        """
        paa = self.get_object()

        retificacao = request.query_params.get('retificacao')
        if retificacao is not None:
            eh_retificacao = retificacao == 'true'
            documento = obter_documento_final_por_retificacao(paa, eh_retificacao)
        else:
            documento = paa.documento_final

        if not documento:
            return Response(
                {"mensagem": "Documento final não gerado"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not documento.concluido:
            return Response(
                {"mensagem": "Documento final não concluído"},
                status=400
            )

        filename = 'documento_final_paa.pdf'
        response = HttpResponse(
            open(documento.arquivo_pdf.path, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response

    @action(detail=True, methods=['get'], url_path='documento-previa',
            permission_classes=[IsAuthenticated])
    def documento_previa(self, request: Request, uuid: str | None = None) -> Response:
        """
        Retorne o arquivo binário da prévia gerada em formato PDF para download.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Um HttpResponse transmitindo os bytes do arquivo em formato anexo.
        """
        paa = self.get_object()
        eh_retificacao = request.query_params.get('retificacao', 'false') == 'true'

        doc = paa.documentopaa_set.filter(
            versao=DocumentoPaa.VersaoChoices.PREVIA,
            retificacao=eh_retificacao,
        ).first()

        if not doc:
            return Response(
                {"mensagem": "Documento prévia não gerado"},
                status=400)

        if not doc.concluido:
            return Response(
                {"mensagem": "Documento prévia não concluído"},
                status=400)

        filename = 'documento_previa_paa.pdf'
        response = HttpResponse(open(doc.arquivo_pdf.path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response

    @action(detail=True, methods=['get'], url_path='status-geracao',
            permission_classes=[IsAuthenticated])
    def satus_geracao(self, request: Request, uuid: str | None = None) -> Response:
        """
        Consulte o estado de processamento dos relatórios do PAA atual.

        Verifica sequencialmente a situação do documento de prévia e do
        documento final.

        Args:
            request: O objeto de requisição HTTP atual.
            uuid: O identificador único do PAA.

        Returns:
            Dicionário especificando o status, versão e descrição do processamento.
        """
        paa = self.get_object()

        doc_previa = paa.documento_previa
        if doc_previa:
            return Response(
                {
                    "mensagem": doc_previa.__str__(),
                    "versao": doc_previa.versao,
                    "status": doc_previa.status_geracao,
                    "retificacao": doc_previa.retificacao,
                },
                status=200
            )
        if paa.status_em_retificacao:
            from sme_ptrf_apps.paa.services.ciclo_retificacao_service import CicloRetificacaoService
            doc_final = CicloRetificacaoService(paa).documento_atual  # None se for doc do ciclo anterior
        else:
            doc_final = paa.documento_final

        if doc_final:
            return Response(
                {
                    "mensagem": doc_final.__str__(),
                    "versao": doc_final.versao,
                    "status": doc_final.status_geracao,
                    "retificacao": doc_final.retificacao,
                },
                status=200
            )

        return Response(
            {"mensagem": "Documento pendente de geração"}, status=200
        )

    @action(detail=True, methods=['post'], url_path='iniciar-retificacao',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def iniciar_retificacao(self, request: Request, uuid: str | None = None) -> Response:
        """
        Inicia o processo de retificação do PAA.

        Recebe no body:
            justificativa (str): Justificativa da retificação (obrigatória).

        Fluxo:
            1. Cria/atualiza uma ReplicaPaa com snapshot do estado atual.
            2. Cria uma AtaPaa do tipo RETIFICACAO com a justificativa informada.
        """
        paa = self.get_object()
        justificativa = request.data.get('justificativa', '').strip()

        service = RetificacaoPaaService(paa=paa, usuario=request.user)

        try:
            service.iniciar_retificacao(justificativa=justificativa)
        except ValidacaoRetificacao as e:
            return Response(
                {'erro': 'iniciar_retificacao', 'mensagem': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'erro': 'erro_retificacao', 'mensagem': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'mensagem': 'Retificação iniciada com sucesso.',
                'paa_uuid': str(paa.uuid),
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], url_path='cancelar-retificacao',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def cancelar_retificacao(self, request: Request, uuid: str | None = None) -> Response:
        """
        Inicia o processo de cancelamento da retificação do PAA.

        Fluxo:
            1. Faz rollback dos registros para o estado salvo em réplica
            2. Remove documento de prévia de retificação
            3. Retorne para o STATUS GERADO, salva Log da réplica e deleta ReplicaPaa corrente.
        """
        paa = self.get_object()

        service = CancelaRetificacaoPaaService(paa=paa, usuario=request.user)

        try:
            service.iniciar_cancelamento_retificacao()
        except ValidacaoCancelaRetificacao as e:
            return Response(
                {'erro': 'cancelar_retificacao', 'mensagem': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'erro': 'erro_cancelamento_retificacao', 'mensagem': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'mensagem': 'Retificação cancelada com sucesso.',
                'paa_uuid': str(paa.uuid),
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'], url_path='paa-retificacao',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def paa_retificacao(self, request: Request, uuid: str | None = None) -> Response:
        """
        Retorne os dados do PAA enriquecidos com o comparativo em relação ao snapshot
        armazenado na réplica, permitindo ao frontend identificar registros
        adicionados, modificados ou removidos desde o início da retificação.

        Retorne 404 se nenhuma retificação foi iniciada para este PAA.
        """

        from sme_ptrf_apps.paa.models import ReplicaPaa
        from sme_ptrf_apps.paa.enums import PaaStatusEnum

        paa = self.get_object()

        try:
            # Valida se existe Réplica
            paa.replica
            # Valida se o PAA foi iniciado para retificação
            Paa.objects.get(uuid=uuid, status=PaaStatusEnum.EM_RETIFICACAO.name)
        except (ReplicaPaa.DoesNotExist, Paa.DoesNotExist):
            return Response(
                {'erro': 'sem_retificacao', 'mensagem': 'Nenhuma retificação iniciada para este PAA.'},
                status=status.HTTP_404_NOT_FOUND
            )

        service = RetificacaoPaaService(paa=paa, usuario=request.user)
        alteracoes = service.identificar_alteracoes()

        serializer = PaaRetificacaoComparativoSerializer(
            paa,
            context={'request': request, 'alteracoes': alteracoes}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
