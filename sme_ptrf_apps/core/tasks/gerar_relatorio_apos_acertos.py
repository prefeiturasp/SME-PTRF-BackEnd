import logging

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.core.models.tasks_celery import TaskCelery
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta

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
def gerar_relatorio_apos_acertos_async(id_task, associacao_uuid, periodo_uuid, usuario=""):
    from sme_ptrf_apps.core.services.analise_prestacao_conta_service import criar_relatorio_apos_acertos_final
    
    try:     
        task = TaskCelery.objects.get(uuid=id_task)
        task.grava_log_concatenado(f'Iniciando a geração relatório após acertos da associacao {associacao_uuid} no período {periodo_uuid}.')
        
        periodo = Periodo.by_uuid(periodo_uuid)
        associacao = Associacao.by_uuid(associacao_uuid)
        prestacao = PrestacaoConta.by_periodo(associacao=associacao, periodo=periodo)
        ultima_analise_pc = prestacao.analises_da_prestacao.order_by('id').last()
        
        criar_relatorio_apos_acertos_final(analise_prestacao_conta=ultima_analise_pc, usuario=usuario)
        
        task.registra_data_hora_finalizacao(f'Finalizada com sucesso a geração do relatório após acertos.')
    except Exception as exc:        
        if gerar_relatorio_apos_acertos_async.request.retries >= MAX_RETRIES:
            mensagem_tentativas_excedidas = 'Tentativas de reprocessamento com falha excedidas'
            task.registra_data_hora_finalizacao(mensagem_tentativas_excedidas)
            raise MaxRetriesExceededError(mensagem_tentativas_excedidas)
        else:
            task.grava_log_concatenado(f'A tentativa {gerar_relatorio_apos_acertos_async.request.retries} de gerar o relatório após acertos falhou. {exc}')
            raise exc
