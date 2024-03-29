from datetime import date
from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.mandatos.api.serializers.validation_serializers.cargo_composicao_serializer import CargosComposicaoPorDataValidateSerializer
from sme_ptrf_apps.mandatos.models.ocupante_cargo import OcupanteCargo
from waffle.mixins import WaffleFlagMixin

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from rest_framework.permissions import IsAuthenticated
from ...models import CargoComposicao, Composicao
from ..serializers import CargoComposicaoSerializer, CargoComposicaoCreateSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

from ...services.cargo_composicao_service import ServicoCargosDaComposicao, ServicoCargosDaDiretoriaExecutiva, ServicoCargosOcupantesComposicao


class CargosComposicoesViewSet(
    WaffleFlagMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet
):
    waffle_flag = "historico-de-membros"
    permission_classes = [IsAuthenticated, PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = CargoComposicao.objects.all()
    serializer_class = CargoComposicaoSerializer
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'partial_update' or self.action == 'create' or self.action == 'update':
            return CargoComposicaoCreateSerializer
        else:
            return CargoComposicaoSerializer

    @action(detail=False, methods=['get'], url_path='cargos-da-composicao',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def cargos_da_composicao(self, request):
        from ..serializers.validation_serializers.cargo_composicao_serializer import CargosComposicaoValidateSerializer

        query = CargosComposicaoValidateSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        composicao_uuid = request.query_params.get('composicao_uuid')
        composicao = Composicao.objects.get(uuid=composicao_uuid)

        servico_cargos_da_composicao = ServicoCargosDaComposicao(composicao=composicao)
        cargos_da_composicao = servico_cargos_da_composicao.get_cargos_da_composicao_ordenado_por_cargo_associacao()

        return Response(cargos_da_composicao, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='cargos-diretoria-executiva',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def cargos_diretoria_executiva(self, request):

        servico_cargos_da_diretoria_executiva = ServicoCargosDaDiretoriaExecutiva()
        cargos_da_diretoria_executiva = servico_cargos_da_diretoria_executiva.get_cargos_diretoria_executiva()

        return Response(cargos_da_diretoria_executiva, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='composicao-por-data',
                permission_classes=[IsAuthenticated & PermissaoApiUe])
    def ocupantes_e_cargos_da_composicao_por_data(self, request):  
        associacao_uuid = request.query_params.get('associacao_uuid')
        data = request.query_params.get('data')

        query = CargosComposicaoPorDataValidateSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        
        associacao = Associacao.objects.get(uuid=associacao_uuid)
        
        try:
            composicao = Composicao.objects.get(
                associacao=associacao,
                data_inicial__lte=data,
                data_final__gte=data
            )
        except ValueError:
            return Response("Composição não encontrada.", status=status.HTTP_400_BAD_REQUEST)
        
        servico_cargos_da_composicao = ServicoCargosOcupantesComposicao()
        
        ocupantes = servico_cargos_da_composicao.get_ocupantes_ordenados_por_cargo(composicao=composicao)
        

        return Response(ocupantes, status=status.HTTP_200_OK)