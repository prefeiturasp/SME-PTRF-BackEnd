import logging

from celery import shared_task
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.sme.services.exporta_consulta_bens_produzidos import ExportacaoConsultaBensProduzidosService
from sme_ptrf_apps.situacao_patrimonial.models import BemProduzidoItem
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.core.models.periodo import Periodo
from itertools import chain
from django.db.models import Q

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=600,
    soft_time_limit=300
)
def exportar_bens_produzidos_adquiridos_async(
    associacao_uuid, 
    especificacao_bem=None, 
    fornecedor=None, 
    acao_uuid=None, 
    conta_uuid=None, 
    periodos_uuid=None, 
    data_inicio=None, 
    data_fim=None, 
    user_id=None,
    filtros_str=None
):
    logger.info("Exportando XLSX de bens produzidos e adquiridos em processamento...")

    try:
        associacao = None
        codigo_eol = None
        dre = None
        
        # Obtem dados da associacao
        try:
            associacao = Associacao.objects.get(uuid=associacao_uuid)
            logger.info(f"Associacao encontrada: {associacao.nome}")
            codigo_eol = associacao.unidade.codigo_eol
            logger.info(f"{associacao.unidade.dre}")
            dre = associacao.unidade.dre.nome
        except Associacao.DoesNotExist:
            logger.error(f"Associação com uuid {associacao_uuid} não encontrada.")
            associacao = None
        
        if associacao is None:
            raise Exception("Associacao nao encontrada")
        
        # Filtrar bens produzidos
        bens_produzidos = BemProduzidoItem.objects.filter(bem_produzido__associacao__uuid=associacao_uuid)
        
        if especificacao_bem:
            bens_produzidos = bens_produzidos.filter(
                especificacao_do_bem__descricao__unaccent__icontains=especificacao_bem
            )
        if fornecedor:
            bens_produzidos = bens_produzidos.filter(
                bem_produzido__despesas__despesa__nome_fornecedor__unaccent__icontains=fornecedor
            )
        if acao_uuid:
            bens_produzidos = bens_produzidos.filter(
                bem_produzido__despesas__rateios__rateio__acao_associacao__uuid=acao_uuid
            ).distinct()
        if conta_uuid:
            bens_produzidos = bens_produzidos.filter(
                bem_produzido__despesas__rateios__rateio__conta_associacao__uuid=conta_uuid
            ).distinct()
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
            bens_produzidos = bens_produzidos.filter(periodo_filters)
        if data_inicio:
            bens_produzidos = bens_produzidos.filter(criado_em__gte=data_inicio)
        if data_fim:
            bens_produzidos = bens_produzidos.filter(criado_em__lte=data_fim)

        # Filtrar bens adquiridos
        bens_adquiridos = RateioDespesa.rateios_completos_de_capital().filter(
            despesa__associacao__uuid=associacao_uuid
        )
        
        if especificacao_bem:
            bens_adquiridos = bens_adquiridos.filter(
                especificacao_material_servico__descricao__unaccent__icontains=especificacao_bem
            )
        if fornecedor:
            bens_adquiridos = bens_adquiridos.filter(
                despesa__nome_fornecedor__unaccent__icontains=fornecedor
            )
        if acao_uuid:
            bens_adquiridos = bens_adquiridos.filter(acao_associacao__uuid=acao_uuid)
        if conta_uuid:
            bens_adquiridos = bens_adquiridos.filter(conta_associacao__uuid=conta_uuid)
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
            bens_adquiridos = bens_adquiridos.filter(periodo_filters)
        if data_inicio:
            bens_adquiridos = bens_adquiridos.filter(despesa__data_documento__gte=data_inicio)
        if data_fim:
            bens_adquiridos = bens_adquiridos.filter(despesa__data_documento__lte=data_fim)

        print(f"Bens produzidos: {bens_produzidos.count()}")
        print(f"Bens adquiridos: {bens_adquiridos.count()}")
        
        # Combinar querysets
        combined_queryset = list(chain(bens_produzidos, bens_adquiridos))
        print(f"Combined queryset: {len(combined_queryset)}")

        # Gerar nome do arquivo
        nome_arquivo = f"bens_produzidos_adquiridos.xlsx"

        logger.info(f"Criando arquivo {nome_arquivo}")
                
        # Criar e executar service de exportação
        params = {
            'queryset': combined_queryset,
            'nome_arquivo': nome_arquivo,
            'data_inicio': data_inicio,
            'data_final': data_fim,
            'user_id': user_id,
            'associacao': associacao,
            'codigo_eol': codigo_eol,
            'dre': dre,
            'filtros_str': filtros_str
        }
        
        ExportacaoConsultaBensProduzidosService(**params).exportar()

    except Exception as e:
        logger.error(f"Erro ao exportar XLSX: {e}")
        raise e

    logger.info("Exportação XLSX finalizada com sucesso.")
