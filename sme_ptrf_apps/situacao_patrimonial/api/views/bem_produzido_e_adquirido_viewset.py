
import logging
from itertools import chain
from waffle.mixins import WaffleFlagMixin

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoItem
from sme_ptrf_apps.situacao_patrimonial.api.serializers import BemProduzidoEAdquiridoSerializer
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.core.models.periodo import Periodo
logger = logging.getLogger(__name__)


class BemAdquiridoProduzidoViewSet(WaffleFlagMixin, ViewSet):
    waffle_flag = "situacao-patrimonial"
    permission_classes = [IsAuthenticated & PermissaoApiUe]

    def list(self, request):
        associacao_uuid = request.query_params.get('associacao_uuid')
        if not associacao_uuid:
            return Response({
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da associação.'
            }, status=status.HTTP_400_BAD_REQUEST)

        especificacao_bem = request.query_params.get('especificacao_bem')
        fornecedor = request.query_params.get('fornecedor')
        acao_uuid = request.query_params.get('acao_associacao_uuid')
        conta_uuid = request.query_params.get('conta_associacao_uuid')
        periodo_uuid = request.query_params.get('periodo_uuid')
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')

        bens_produzidos = BemProduzidoItem.objects.filter(bem_produzido__associacao__uuid=associacao_uuid)
        bens_produzidos = self.filtrar_bens_produzidos(
            bens_produzidos, especificacao_bem, fornecedor, acao_uuid, conta_uuid, periodo_uuid, data_inicio, data_fim
        )

        bens_adquiridos = RateioDespesa.rateios_completos_de_capital().filter(despesa__associacao__uuid=associacao_uuid)
        bens_adquiridos = self.filtrar_bens_adquiridos(
            bens_adquiridos, especificacao_bem, fornecedor, acao_uuid, conta_uuid, periodo_uuid, data_inicio, data_fim
        )

        combined = list(chain(bens_produzidos, bens_adquiridos))

        paginator = CustomPagination()
        page = paginator.paginate_queryset(combined, request)
        serializer = BemProduzidoEAdquiridoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def filtrar_bens_produzidos(self, queryset, especificacao_bem, fornecedor, acao_uuid, conta_uuid, periodo_uuid, data_inicio, data_fim):
        if especificacao_bem:
            queryset = queryset.filter(especificacao_do_bem__descricao__unaccent__icontains=especificacao_bem)
        if fornecedor:
            queryset = queryset.filter(
                bem_produzido__despesas__despesa__nome_fornecedor__unaccent__icontains=fornecedor)
        if acao_uuid:
            queryset = queryset.filter(
                bem_produzido__despesas__rateios__rateio__acao_associacao__uuid=acao_uuid).distinct()
        if conta_uuid:
            queryset = queryset.filter(
                bem_produzido__despesas__rateios__rateio__conta_associacao__uuid=conta_uuid).distinct()
        if periodo_uuid:
            try:
                periodo = Periodo.objects.get(uuid=periodo_uuid)
                data_inicio = periodo.data_inicio_realizacao_despesas
                data_fim = periodo.data_fim_realizacao_despesas
            except Periodo.DoesNotExist:
                pass
        if data_inicio:
            queryset = queryset.filter(criado_em__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(criado_em__lte=data_fim)
        return queryset

    def filtrar_bens_adquiridos(self, queryset, especificacao_bem, fornecedor, acao_uuid, conta_uuid, periodo_uuid, data_inicio, data_fim):
        if especificacao_bem:
            queryset = queryset.filter(especificacao_material_servico__descricao__unaccent__icontains=especificacao_bem)
        if fornecedor:
            queryset = queryset.filter(despesa__nome_fornecedor__unaccent__icontains=fornecedor)
        if acao_uuid:
            queryset = queryset.filter(acao_associacao__uuid=acao_uuid)
        if conta_uuid:
            queryset = queryset.filter(conta_associacao__uuid=conta_uuid)
        if periodo_uuid:
            try:
                periodo = Periodo.objects.get(uuid=periodo_uuid)
                data_inicio = periodo.data_inicio_realizacao_despesas
                data_fim = periodo.data_fim_realizacao_despesas
            except Periodo.DoesNotExist:
                pass
        if data_inicio:
            queryset = queryset.filter(despesa__data_documento__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(despesa__data_documento__lte=data_fim)
        return queryset
