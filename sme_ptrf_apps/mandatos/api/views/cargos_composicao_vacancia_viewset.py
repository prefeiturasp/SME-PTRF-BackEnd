from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import mixins, status, serializers
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from waffle.mixins import WaffleFlagMixin
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from sme_ptrf_apps.core.models.associacao import Associacao
from ...exceptions import CargoComposicaoVacanciaValidationError
from ...models import CargoComposicaoVacancia, ComposicaoVacancia, Mandato
from ..serializers import (
    CargoComposicaoVacanciaSerializer,
    CargoComposicaoVacanciaCreateSerializer,
    RegistrarSaidaSerializer,
    CargoComposicaoVacanciaEditarOcupanteSerializer
)
from ...services import ServicoHistoricoCargoComposicao

from .docs.cargos_composicao_vacancia_docs import DOCS


@extend_schema_view(**DOCS)
class CargosComposicoesVacanciaViewSet(WaffleFlagMixin,
                                       mixins.ListModelMixin,
                                       mixins.RetrieveModelMixin,
                                       mixins.CreateModelMixin,
                                       mixins.UpdateModelMixin,
                                       GenericViewSet):
    waffle_flag = "historico-de-membros-v2"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = CargoComposicaoVacancia.objects.all()
    serializer_class = CargoComposicaoVacanciaSerializer
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CargoComposicaoVacanciaCreateSerializer
        if self.action in ('update', 'partial_update'):
            return CargoComposicaoVacanciaEditarOcupanteSerializer
        return CargoComposicaoVacanciaSerializer

    def _get_composicao_vacancia_ou_404(self, composicao_uuid: str) -> ComposicaoVacancia:
        """Busca a ComposicaoVacancia por uuid, convertendo DoesNotExist/uuid inválido em Http404."""
        try:
            return ComposicaoVacancia.by_uuid(composicao_uuid)
        except (ComposicaoVacancia.DoesNotExist, ValidationError):
            raise Http404('Composição não encontrada')

    @action(detail=False, methods=['get'], url_path='composicao-vigente',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def composicao_vigente(self, request):
        """Retorna o uuid da ComposicaoVacancia do par (associação, mandato), criando-a se necessário."""
        associacao = Associacao.by_uuid(request.query_params.get('associacao_uuid'))
        mandato = Mandato.by_uuid(request.query_params.get('mandato_uuid'))

        composicao_vacancia = ServicoHistoricoCargoComposicao.get_or_create_composicao_vacancia(
            associacao=associacao,
            mandato=mandato
        )
        return Response({'uuid': str(composicao_vacancia.uuid)}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='registrar-saida',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def registrar_saida(self, request, uuid=None):
        """Registra a saída do ocupante vigente do cargo, a partir da data_saida do payload."""
        cargo_composicao_vacancia = self.get_object()

        serializer = RegistrarSaidaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ServicoHistoricoCargoComposicao.registrar_saida(
                cargo_composicao_vacancia=cargo_composicao_vacancia,
                data_saida=serializer.validated_data.get('data_saida')
            )
        except CargoComposicaoVacanciaValidationError as e:
            raise serializers.ValidationError(e.detail)

        return Response(
            CargoComposicaoVacanciaSerializer(cargo_composicao_vacancia).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='composicao-por-data',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def composicao_por_data(self, request):
        """Retorna o snapshot da composição (por cargo) resolvida por composicao_uuid ou associacao_uuid+data."""
        composicao_vacancia = ServicoHistoricoCargoComposicao.get_composicao_vacancia_por_uuid_ou_associacao_e_data(
            composicao_uuid=request.query_params.get('composicao_uuid'),
            associacao_uuid=request.query_params.get('associacao_uuid'),
            data=request.query_params.get('data'),
        )

        if not composicao_vacancia:
            return Response({'erro': 'Composição não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        snapshot = ServicoHistoricoCargoComposicao.get_snapshot_da_composicao_em_data(
            composicao_vacancia=composicao_vacancia,
            data=request.query_params.get('data'),
        )

        resultado = {
            cargo: CargoComposicaoVacanciaSerializer(registro).data if registro else None
            for cargo, registro in snapshot.items()
        }

        return Response(resultado, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='datas-de-alteracao',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def datas_de_alteracoes_na_composicao(self, request):
        """Retorna as datas (marcos) de alteração da composição."""
        composicao_vacancia = self._get_composicao_vacancia_ou_404(request.query_params.get('composicao_uuid'))

        datas = ServicoHistoricoCargoComposicao.get_datas_de_alteracao_da_composicao(composicao_vacancia)
        datas_formatos = [d.isoformat() for d in datas]
        return Response(datas_formatos, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='cancelar-saida',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def cancelar_saida(self, request, uuid=None):
        """Reverte a saída do registro, devolvendo-o ao estado vigente."""
        cargo_composicao_vacancia = self.get_object()

        try:
            ServicoHistoricoCargoComposicao.cancelar_saida(cargo_composicao_vacancia)
        except CargoComposicaoVacanciaValidationError as e:
            raise serializers.ValidationError(e.detail)

        return Response(
            CargoComposicaoVacanciaSerializer(cargo_composicao_vacancia).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['patch'], url_path='corrigir-saida',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def corrigir_data_saida(self, request, uuid=None):
        """Corrige a data de uma saída já registrada, a partir da data_saida do payload."""
        cargo_composicao_vacancia = self.get_object()

        serializer = RegistrarSaidaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ServicoHistoricoCargoComposicao.corrigir_data_saida(
                cargo_composicao_vacancia,
                serializer.validated_data.get('data_saida')
            )
        except CargoComposicaoVacanciaValidationError as e:
            raise serializers.ValidationError(e.detail)

        return Response(
            CargoComposicaoVacanciaSerializer(cargo_composicao_vacancia).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='timeline',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def timeline(self, request):
        """Retorna o histórico completo de um cargo (ocupados e vagos), ordenado por data.

        Query params: composicao_uuid, cargo_associacao_uuid.
        """
        composicao_vacancia = self._get_composicao_vacancia_ou_404(request.query_params.get('composicao_uuid'))
        registros = ServicoHistoricoCargoComposicao.get_timeline_do_cargo(
            composicao_vacancia=composicao_vacancia,
            cargo_associacao=request.query_params.get('cargo_associacao_uuid')
        )

        return Response(
            CargoComposicaoVacanciaSerializer(registros, many=True).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='cargos-da-composicao',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def cargos_da_composicao(self, request):
        """Monta os cargos da composição no formato consumido pelo frontend da v2.

        Query params: composicao_uuid, data (opcional, padrão hoje).
        """
        composicao_vacancia = self._get_composicao_vacancia_ou_404(request.query_params.get('composicao_uuid'))

        cargos = ServicoHistoricoCargoComposicao.monta_cargos_da_composicao(
            composicao_vacancia,
            request.query_params.get('data')
        )

        return Response(cargos, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='cancelar-entrada',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def cancelar_entrada(self, request, uuid=None):
        """Desfaz a entrada vigente do cargo, restaurando o estado anterior."""
        cargo_composicao_vacancia = self.get_object()

        try:
            ServicoHistoricoCargoComposicao.cancelar_entrada(cargo_composicao_vacancia)
        except CargoComposicaoVacanciaValidationError as e:
            raise serializers.ValidationError(e.detail)

        return Response(status=status.HTTP_204_NO_CONTENT)
