import logging

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from sme_ptrf_apps.core.models.demonstrativo_financeiro import DemonstrativoFinanceiro
from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from sme_ptrf_apps.core.services.demonstrativo_financeiro_pdf_service import gerar_arquivo_demonstrativo_financeiro_pdf
from sme_ptrf_apps.core.services.recuperacao_dados_persistindos_demo_financeiro_service import \
    RecuperaDadosDemoFinanceiro
from sme_ptrf_apps.core.models.tasks_celery import TaskCelery

logger = logging.getLogger(__name__)

MAX_RETRIES = 8


@shared_task(
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': MAX_RETRIES},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    time_limit=600,
    soft_time_limit=300
)
def gerar_demonstrativo_financeiro_async(id_task, prestacao_conta_uuid, periodo_uuid):
    try:
        task = TaskCelery.objects.get(uuid=id_task)
        logger.info('Iniciando task gerar_demonstrativo_financeiro_async.')

        prestacao = PrestacaoConta.objects.get(uuid=prestacao_conta_uuid)
        periodo = Periodo.objects.get(uuid=periodo_uuid)
        contas = prestacao.contas_ativas_no_periodo()

        task.grava_log_concatenado(
            f'Iniciando a geração do demonstrativo financeiro da pc de uuid {prestacao_conta_uuid} e do periodo {periodo}.')

        for conta_associacao in contas:
            task.grava_log_concatenado(
                f'Iniciando criação do demonstrativo financeiro para a conta {conta_associacao} - {conta_associacao.uuid} e o período {periodo}.')

            demonstrativo = DemonstrativoFinanceiro.objects.get(
                conta_associacao_id=conta_associacao.id,
                prestacao_conta_id=prestacao.id
            )

            dados_recuperados = RecuperaDadosDemoFinanceiro(demonstrativo=demonstrativo).dados_formatados

            gerar_arquivo_demonstrativo_financeiro_pdf(dados_recuperados, demonstrativo)

            demonstrativo.arquivo_concluido()

            task.grava_log_concatenado(
                f'Demonstrativo financeiro criado para a conta {conta_associacao} - {conta_associacao.uuid}.')
            task.grava_log_concatenado(f'Demonstrativo financeiro arquivo {demonstrativo.uuid}.')

        logger.info('Task gerar_demonstrativo_financeiro_async finalizada.')

        task.registra_data_hora_finalizacao(f'Finalizada com sucesso a geração do demonstrativo financeiro.')
    except Exception as exc:
        if gerar_demonstrativo_financeiro_async.request.retries >= MAX_RETRIES:
            mensagem_tentativas_excedidas = 'Tentativas de reprocessamento com falha excedidas.'
            task.registra_data_hora_finalizacao(mensagem_tentativas_excedidas)
            raise MaxRetriesExceededError(mensagem_tentativas_excedidas)
        else:
            task.grava_log_concatenado(
                f'A tentativa {gerar_demonstrativo_financeiro_async.request.retries} de gerar o demonstrativo financeiro falhou. {exc}')
            raise exc
