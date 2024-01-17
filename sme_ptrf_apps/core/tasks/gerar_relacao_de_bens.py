import logging
import traceback

from celery import shared_task, current_task
from celery.exceptions import MaxRetriesExceededError

from sme_ptrf_apps.core.models import PrestacaoConta, RelacaoBens, TaskCelery
from sme_ptrf_apps.core.services.relacao_bens import _retornar_dados_relatorio_relacao_de_bens
from sme_ptrf_apps.core.services.relacao_bens_pdf_service import gerar_arquivo_relacao_de_bens_pdf
from sme_ptrf_apps.core.services.prestacao_conta_service import PrestacaoContaService

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


@shared_task(
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': MAX_RETRIES},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    time_limit=600,
    soft_time_limit=300
)
def gerar_relacao_bens_async(id_task, prestacao_conta_uuid):
    tentativa = current_task.request.retries + 1

    task = None
    try:
        task = TaskCelery.objects.get(uuid=id_task)
        logger.info(f'Iniciando task gerar_relacao_bens_async, tentativa {tentativa}')

        pc_service = PrestacaoContaService.from_prestacao_conta_uuid(prestacao_conta_uuid)

        if not pc_service.requer_gerar_documentos:
            logger.info(f'Prestação de conta {pc_service.prestacao.uuid} não requer geração de documentos. Relação de bens não será gerada.')
            return

        prestacao = pc_service.prestacao

        relacao_bens = prestacao.relacoes_de_bens_da_prestacao.filter(versao=RelacaoBens.VERSAO_FINAL)

        for relacao in relacao_bens:
            dados = _retornar_dados_relatorio_relacao_de_bens(relacao)

            if dados:
                gerar_arquivo_relacao_de_bens_pdf(dados, relacao)
                relacao.arquivo_concluido()
                task.grava_log_concatenado(f'Arquivo relação bens PDF gerado para a conta {relacao.conta_associacao}.')
            else:
                task.grava_log_concatenado(f'Dados persistidos da relação de bens {relacao} não encontrados.')

        logger.info('Task gerar_arquivo_final_relacao_bens_async finalizada')
        task.registra_data_hora_finalizacao(f'Finalizada com sucesso a geração da relação de bens.')
    except Exception as exc:
        if task:
            task.grava_log_concatenado(f'A tentativa {tentativa} de gerar a relação de bens falhou. {exc}')

        if tentativa > MAX_RETRIES:
            traceback_info = traceback.format_exc()
            mensagem_tentativas_excedidas = f'Tentativas de reprocessamento com falha excedidas para a relação de bens. Detalhes do erro: {exc}\n{traceback_info}'
            logger.error(mensagem_tentativas_excedidas)

            if task:
                task.registra_data_hora_finalizacao(mensagem_tentativas_excedidas)

            raise MaxRetriesExceededError(mensagem_tentativas_excedidas)
        else:
            raise exc

