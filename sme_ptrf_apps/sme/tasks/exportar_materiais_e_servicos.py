import logging

from celery import shared_task
from sme_ptrf_apps.despesas.models.especificacao_material_servico import EspecificacaoMaterialServico
from sme_ptrf_apps.despesas.models.tipo_custeio import TipoCusteio
from sme_ptrf_apps.sme.services.exporta_materiais_e_servicos_service import ExportacoesDadosMateriaisEServicosService


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_materiais_e_servicos_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")

    queryset = EspecificacaoMaterialServico.objects.all()
    queryset_tipo_custeio = TipoCusteio.objects.all()
    try:
        logger.info("Criando arquivo %s especificacoes_materiais_servicos.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }

        ExportacoesDadosMateriaisEServicosService(
            **params,
            nome_arquivo='especificacoes_materiais_servicos.csv'
        ).exporta_materiais_e_servicos()

        params['queryset'] = queryset_tipo_custeio
        logger.info("Criando arquivo %s tipos_de_custeio.csv")
        ExportacoesDadosMateriaisEServicosService(
            **params,
            nome_arquivo='tipos_de_custeio.csv'
        ).exporta_tipos_de_custeio()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")