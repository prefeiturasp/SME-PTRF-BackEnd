import logging

from datetime import datetime
from django.http import Http404
from django.db.models import Q

from waffle.mixins import WaffleFlagMixin
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import (
    PermissaoAPITodosComLeituraOuGravacao,
    PermissaoApiUe
)
from sme_ptrf_apps.paa.api.serializers.paa_serializer import PaaSerializer, PaaUpdateSerializer
from sme_ptrf_apps.paa.api.serializers.receita_prevista_paa_serializer import ReceitaPrevistaPaaSerializer
from sme_ptrf_apps.paa.models import Paa
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.paa.services.paa_service import PaaService, ImportacaoConfirmacaoNecessaria
from sme_ptrf_apps.paa.services.receitas_previstas_paa_service import SaldosPorAcaoPaaService
from sme_ptrf_apps.paa.services.resumo_prioridades_service import ResumoPrioridadesService

logger = logging.getLogger(__name__)


class PaaViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "paa"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Paa.objects.all()
    serializer_class = PaaSerializer
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'delete', 'patch']

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return PaaUpdateSerializer
        else:
            return PaaSerializer

    def get_queryset(self):
        qs = self.queryset
        associacao = self.request.query_params.get('associacao_uuid', None)

        if associacao is not None:
            qs = qs.filter(associacao__uuid=associacao)

        return qs

    @action(detail=False, methods=['get'], url_path='download-pdf-levantamento-prioridades',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def download_levantamento_prioridades_paa(self, request):
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
    def desativar_atualizacao_saldo(self, request, uuid):
        instance = self.get_object()
        associacao = instance.associacao

        saldos_por_acao_paa_service = SaldosPorAcaoPaaService(paa=instance, associacao=associacao)
        receitas_previstas = saldos_por_acao_paa_service.congelar_saldos()

        serializer = ReceitaPrevistaPaaSerializer(receitas_previstas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='ativar-atualizacao-saldo',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def ativar_atualizacao_saldo(self, request, uuid):
        instance = self.get_object()
        associacao = instance.associacao

        saldos_por_acao_paa_service = SaldosPorAcaoPaaService(paa=instance, associacao=associacao)
        receitas_previstas = saldos_por_acao_paa_service.descongelar_saldos()

        serializer = ReceitaPrevistaPaaSerializer(receitas_previstas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
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
    def resumo_prioridades(self, request, uuid=None):
        result = ResumoPrioridadesService(self.get_object()).resumo_prioridades()
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='paas-anteriores',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def paa_anteriores(self, request, uuid=None):
        paa_atual = self.get_object()
        paas_anteriores = self.queryset.filter(
            periodo_paa__data_inicial__lt=paa_atual.periodo_paa.data_inicial,
            associacao=paa_atual.associacao
        ).order_by('-periodo_paa__data_inicial')

        serializer = PaaSerializer(paas_anteriores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='importar-prioridades/(?P<uuid_paa_anterior>[a-f0-9-]+)',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def importar_prioridades(self, request, uuid=None, uuid_paa_anterior=None):
        """
            Importar prioridades de PAA anterior.

            Essa action pode ser usada para importar as prioridades de PAA anterior
            para o PAA atual.

            - uuid_paa_anterior: uuid do PAA anterior para importar as prioridades.

            Retorna um dicionário com a mensagem de sucesso e a quantidade de
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
    def receitas_previstas(self, request, uuid=None):
        from sme_ptrf_apps.core.api.serializers.acao_associacao_serializer import AcaoAssociacaoRetrieveSerializer

        paa = self.get_object()
        acoes_associacoes = paa.associacao.acoes.all()

        serializer_acao_associacao = AcaoAssociacaoRetrieveSerializer(acoes_associacoes, many=True)
        for acao_assoc in serializer_acao_associacao.data:
            acao_assoc['receitas_previstas_paa'] = ReceitaPrevistaPaaSerializer(
                paa.receitaprevistapaa_set.filter(
                    acao_associacao__acao__uuid=str(acao_assoc['acao']['uuid'])
                ),
                many=True).data

        return Response(serializer_acao_associacao.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='objetivos',
            permission_classes=[IsAuthenticated])
    def objetivos(self, request, uuid=None):
        from sme_ptrf_apps.paa.api.serializers.objetivo_paa_serializer import ObjetivoPaaSerializer
        from sme_ptrf_apps.paa.models.objetivo_paa import ObjetivoPaa

        paa = self.get_object()

        objetivos = ObjetivoPaa.objects.filter(Q(paa__isnull=True) | Q(paa=paa))

        serializer = ObjetivoPaaSerializer(objetivos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
