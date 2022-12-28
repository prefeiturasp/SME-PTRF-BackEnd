import logging

from celery import shared_task
from sme_ptrf_apps.receitas.models.receita import Receita
from sme_ptrf_apps.sme.services.exporta_dados_creditos_service import ExportacoesDadosCreditosService
from sme_ptrf_apps.dre.models import AnaliseConsolidadoDre


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def exportar_receitas_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")
    queryset = Receita.objects.all()
    try:
        logger.info("Criando arquivo %s creditos_principal.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }
        ExportacoesDadosCreditosService(
            **params,
            nome_arquivo='creditos_principal.csv'
        ).exporta_creditos_principal()
        logger.info("Criando arquivo %s creditos_motivo_estorno.csv")
        ExportacoesDadosCreditosService(
            **params,
            nome_arquivo='creditos_motivos_estorno.csv'
        ).exporta_creditos_motivos_estorno()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_relatorio_devolucao_acertos_async(analise_consolidado_uuid, username, previa):
    logger.info(f"Iniciando geração do relatório de devolução de acertos da sme async")

    from sme_ptrf_apps.dre.services import RelatorioDevolucaoAcertos

    analise_consolidado = AnaliseConsolidadoDre.by_uuid(analise_consolidado_uuid)

    relatorio = RelatorioDevolucaoAcertos(
        analise_consolidado=analise_consolidado,
        username=username,
        previa=previa
    )

    relatorio.gerar_arquivo_relatorio_devolucao_acertos()


    logger.info("Finalizando geração do relatório de devolução de acertos da sme async")
