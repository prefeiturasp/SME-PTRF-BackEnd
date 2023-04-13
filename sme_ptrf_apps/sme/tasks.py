import logging

from celery import shared_task
from sme_ptrf_apps.core.models.devolucao_ao_tesouro import DevolucaoAoTesouro
from sme_ptrf_apps.core.models.solicitacao_devolucao_ao_tesouro import SolicitacaoDevolucaoAoTesouro
from sme_ptrf_apps.despesas.models.especificacao_material_servico import EspecificacaoMaterialServico
from sme_ptrf_apps.despesas.models.tipo_custeio import TipoCusteio
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from sme_ptrf_apps.receitas.models.receita import Receita
from sme_ptrf_apps.sme.services.exporta_dados_creditos_service import ExportacoesDadosCreditosService
from sme_ptrf_apps.dre.models import AnaliseConsolidadoDre
from sme_ptrf_apps.sme.services.exporta_materiais_e_servicos_service import ExportacoesDadosMateriaisEServicosService
from sme_ptrf_apps.sme.services.exporta_status_prestacoes_conta_service import ExportacoesStatusPrestacoesContaService
from sme_ptrf_apps.sme.services.exporta_saldo_final_periodo_pc_service import ExportacoesDadosSaldosFinaisPeriodoService
from sme_ptrf_apps.sme.services.exporta_relacao_bens_pc import ExportacoesDadosRelacaoBensService
from sme_ptrf_apps.sme.services.exporta_devolucao_tesouro_prestacoes_conta import ExportacoesDevolucaoTesouroPrestacoesContaService
from sme_ptrf_apps.sme.services.exporta_rateios_service import ExportacoesRateiosService
from sme_ptrf_apps.core.models import FechamentoPeriodo, RelacaoBens
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_INATIVO


logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
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


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300000
)
def exportar_saldos_finais_periodo_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")

    queryset = FechamentoPeriodo.objects.all().order_by('id')

    try:
        logger.info("Criando arquivo %s pcs_saldo_final_periodo.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }

        ExportacoesDadosSaldosFinaisPeriodoService(
            **params,
            nome_arquivo='pcs_saldo_final_periodo.csv'
        ).exporta_saldos_finais_periodos()
    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_relacao_bens_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")

    queryset = RelacaoBens.objects.all().order_by('id')

    try:
        logger.info("Criando arquivo %s pcs_relacoes_bens.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }

        ExportacoesDadosRelacaoBensService(
            **params,
            nome_arquivo='pcs_relacoes_bens.csv'
        ).exporta_relacao_bens()
    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_status_prestacoes_contas_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")

    queryset = PrestacaoConta.objects.all().order_by('criado_em')

    try:
        logger.info("Criando arquivo %s status_prestacoes_de_contas.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }

        ExportacoesStatusPrestacoesContaService(
            **params,
            nome_arquivo='status_prestacoes_de_contas.csv'
        ).exporta_status_prestacoes_conta()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=30000
)
def exportar_devolucoes_ao_tesouro_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")

    queryset = SolicitacaoDevolucaoAoTesouro.objects.all().order_by('criado_em')

    try:
        logger.info("Criando arquivo %s pcs_devolucoes_tesouro.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }

        ExportacoesDevolucaoTesouroPrestacoesContaService(
            **params,
            nome_arquivo='pcs_devolucoes_tesouro.csv'
        ).exporta_devolucao_tesouro_pc()

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
def exportar_devolucoes_ao_tesouro_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")

    queryset = DevolucaoAoTesouro.objects.all().order_by('criado_em')

    try:
        logger.info("Criando arquivo %s pcs_devolucoes_tesouro.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }

        ExportacoesDevolucaoTesouroPrestacoesContaService(
            **params,
            nome_arquivo='pcs_devolucoes_tesouro.csv'
        ).exporta_devolucao_tesouro_pc()

    except Exception as e:
        logger.error(f"Erro ao exportar csv: {e}")
        raise e

    logger.info("Exportação csv finalizada com sucesso.")

@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300000
)
def exportar_rateios_async(data_inicio, data_final, username):
    logger.info("Exportando csv em processamento...")

    queryset = RateioDespesa.objects.exclude(status=STATUS_INATIVO).order_by('id')

    try:
        logger.info("Criando arquivo %s despesas_classificacao_item.csv")
        params = {
            'queryset': queryset,
            'data_inicio': data_inicio,
            'data_final': data_final,
            'user': username,
        }

        ExportacoesRateiosService(
            **params,
            nome_arquivo='despesas_classificacao_item.csv'
        ).exporta_rateios()

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
