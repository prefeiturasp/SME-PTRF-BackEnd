
import logging
import uuid
from itertools import chain
from waffle.mixins import WaffleFlagMixin

from django.db.models import Q
from django.core.exceptions import ValidationError

from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
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
        periodos_uuid = request.query_params.get('periodos_uuid')

        if periodos_uuid:
            try:
                periodos_uuid = [uuid.UUID(u.strip()) for u in periodos_uuid.split(",") if u.strip()]
            except Exception:
                raise ValidationError("Parâmetro período inválido. Deve ser uma lista de UUIDs separadas por vírgula.")

        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')

        bens_produzidos = BemProduzidoItem.objects.filter(bem_produzido__associacao__uuid=associacao_uuid)
        bens_produzidos = self.filtrar_bens_produzidos(
            bens_produzidos, especificacao_bem, fornecedor, acao_uuid, conta_uuid, periodos_uuid, data_inicio, data_fim
        )

        bens_adquiridos = RateioDespesa.rateios_completos_de_capital().filter(despesa__associacao__uuid=associacao_uuid)
        bens_adquiridos = self.filtrar_bens_adquiridos(
            bens_adquiridos, especificacao_bem, fornecedor, acao_uuid, conta_uuid, periodos_uuid, data_inicio, data_fim
        )

        combined = list(chain(bens_produzidos, bens_adquiridos))

        paginator = CustomPagination()
        page = paginator.paginate_queryset(combined, request)
        serializer = BemProduzidoEAdquiridoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def filtrar_bens_produzidos(self, queryset, especificacao_bem, fornecedor, acao_uuid, conta_uuid, periodos_uuid, data_inicio, data_fim):
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
        if periodos_uuid:
            periodos = Periodo.objects.filter(uuid__in=periodos_uuid)
            periodo_filters = Q()

            for periodo in periodos:
                if periodo.data_inicio_realizacao_despesas and periodo.data_fim_realizacao_despesas:
                    periodo_filters |= Q(
                        criado_em__gte=periodo.data_inicio_realizacao_despesas,
                        criado_em__lte=periodo.data_fim_realizacao_despesas
                    )
                elif periodo.data_inicio_realizacao_despesas:
                    periodo_filters |= Q(
                        criado_em__gte=periodo.data_inicio_realizacao_despesas,
                    )

            queryset = queryset.filter(periodo_filters)
        if data_inicio:
            queryset = queryset.filter(criado_em__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(criado_em__lte=data_fim)
        return queryset

    def filtrar_bens_adquiridos(self, queryset, especificacao_bem, fornecedor, acao_uuid, conta_uuid, periodos_uuid, data_inicio, data_fim):
        if especificacao_bem:
            queryset = queryset.filter(especificacao_material_servico__descricao__unaccent__icontains=especificacao_bem)
        if fornecedor:
            queryset = queryset.filter(despesa__nome_fornecedor__unaccent__icontains=fornecedor)
        if acao_uuid:
            queryset = queryset.filter(acao_associacao__uuid=acao_uuid)
        if conta_uuid:
            queryset = queryset.filter(conta_associacao__uuid=conta_uuid)
        if periodos_uuid:
            periodos = Periodo.objects.filter(uuid__in=periodos_uuid)
            periodo_filters = Q()
            for periodo in periodos:
                if periodo.data_inicio_realizacao_despesas and periodo.data_fim_realizacao_despesas:
                    periodo_filters |= Q(
                        despesa__data_documento__gte=periodo.data_inicio_realizacao_despesas,
                        despesa__data_documento__lte=periodo.data_fim_realizacao_despesas
                    )
                elif periodo.data_inicio_realizacao_despesas:
                    periodo_filters |= Q(
                        despesa__data_documento__gte=periodo.data_inicio_realizacao_despesas,
                    )

            queryset = queryset.filter(periodo_filters)
        if data_inicio:
            queryset = queryset.filter(despesa__data_documento__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(despesa__data_documento__lte=data_fim)
        return queryset
