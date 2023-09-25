import logging

from celery import shared_task

from sme_ptrf_apps.core.models import (
    Periodo,
    Unidade,
)

from sme_ptrf_apps.dre.models import (
    AtaParecerTecnico,
)

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limit=333333,
    soft_time_limit=333333
)
def gerar_arquivo_ata_parecer_tecnico_async(ata_uuid, dre_uuid, periodo_uuid, usuario, parcial):
    logger.info(f'Iniciando a geração da Ata de Parecer Técnico Async. DRE {dre_uuid} e Período {periodo_uuid}')
    from ..services import gerar_arquivo_ata_parecer_tecnico

    ata = AtaParecerTecnico.by_uuid(ata_uuid)
    dre = Unidade.dres.get(uuid=dre_uuid)
    periodo = Periodo.by_uuid(periodo_uuid)

    arquivo_ata = gerar_arquivo_ata_parecer_tecnico(ata=ata, dre=dre, periodo=periodo, usuario=usuario, parcial=parcial)

    if arquivo_ata is not None:
        logger.info(f'Arquivo ata parecer técnico: {arquivo_ata} gerado com sucesso.')
