import logging

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from sme_ptrf_apps.core.models import PrestacaoConta, RelacaoBens, TaskCelery
from sme_ptrf_apps.core.services.relacao_bens import _retornar_dados_relatorio_relacao_de_bens
from sme_ptrf_apps.core.services.relacao_bens_pdf_service import gerar_arquivo_relacao_de_bens_pdf

logger = logging.getLogger(__name__)

MAX_RETRIES = 8


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=600,
    soft_time_limit=300
)
def gerar_relacao_bens_async(id_task, prestacao_conta_uuid):
    try:
        task = TaskCelery.objects.get(uuid=id_task)
        logger.info('Iniciando task gerar_relacao_bens_async')

        prestacao = PrestacaoConta.objects.get(uuid=prestacao_conta_uuid)

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
        if gerar_relacao_bens_async.request.retries >= MAX_RETRIES:
            mensagem_tentativas_excedidas = 'Tentativas de reprocessamento com falha excedidas.'
            task.registra_data_hora_finalizacao(mensagem_tentativas_excedidas)
            raise MaxRetriesExceededError(mensagem_tentativas_excedidas)
        else:
            task.grava_log_concatenado(
                f'A tentativa {gerar_relacao_bens_async.request.retries} de gerar a relação de bens falhou. {exc}')
            raise exc
