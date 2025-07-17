import logging

from waffle.mixins import WaffleFlagMixin

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.despesas.models.despesa import Despesa

from sme_ptrf_apps.despesas.models.rateio_despesa import RateioDespesa
from sme_ptrf_apps.users.permissoes import PermissaoApiUe

from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoDespesa, BemProduzidoRateio
from sme_ptrf_apps.situacao_patrimonial.api.serializers import DespesaSituacaoPatrimonialSerializer

from django.db.models.functions import Coalesce
from django.db.models import Sum, F, OuterRef, Subquery, DecimalField, ExpressionWrapper, Q

logger = logging.getLogger(__name__)


class DespesaSituacaoPatrimonialViewSet(WaffleFlagMixin, ModelViewSet):
    waffle_flag = "situacao-patrimonial"
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    lookup_field = 'uuid'
    queryset = Despesa.objects.all()
    serializer_class = DespesaSituacaoPatrimonialSerializer
    pagination_class = CustomPagination
    http_method_names = ['get']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        bem_produzido_uuid = self.request.query_params.get('bem_produzido_uuid')
        if not bem_produzido_uuid:
            bem_produzido_uuid = self.kwargs.get('bem_produzido_uuid')
        if bem_produzido_uuid:
            context['bem_produzido_uuid'] = bem_produzido_uuid
        return context

    def get_queryset(self):
        qs = Despesa.objects.exclude(status='INATIVO').all()
        
        search = self.request.query_params.get('search')
        if search is not None and search != '':
            qs = qs.filter(
                pk__in=Subquery(
                    qs.filter(rateios__especificacao_material_servico__descricao__unaccent__icontains=search).distinct("uuid").values('pk')
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
        
        bem_produzido_rateio_sum = BemProduzidoRateio.objects.filter(
            rateio=OuterRef('pk')
        ).values('rateio').annotate(
            total_utilizado=Sum('valor_utilizado')
        ).values('total_utilizado')[:1]

        bem_produzido_despesa_sum = BemProduzidoDespesa.objects.filter(
            despesa=OuterRef('pk')
        ).values('despesa').annotate(
            total_utilizado=Sum('valor_recurso_proprio_utilizado')
        ).values('total_utilizado')[:1]

        qs = qs.annotate(
            total_utilizado_despesa=Subquery(bem_produzido_despesa_sum, output_field=DecimalField()),
            restante_recursos_proprios=ExpressionWrapper(
                F('valor_recursos_proprios') - Coalesce(F('total_utilizado_despesa'), 0),
                output_field=DecimalField()
            )
        ).filter(
            Q(  # se houver recurso próprio restante na despesa
                restante_recursos_proprios__gt=0
            ) | Q(  # ou se algum rateio ainda tiver valor a ser utilizado
                rateios__in=RateioDespesa.objects.annotate(
                    total_utilizado=Subquery(bem_produzido_rateio_sum, output_field=DecimalField()),
                    restante=ExpressionWrapper(
                        F('valor_rateio') - Coalesce(F('total_utilizado'), 0),
                        output_field=DecimalField()
                    )
                ).filter(restante__gt=0)
            )
        ) 
        return qs.distinct("uuid")
