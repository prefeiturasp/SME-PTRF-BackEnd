import logging

from sme_ptrf_apps.core.models import DemonstrativoFinanceiro
from sme_ptrf_apps.core.services.dados_demo_financeiro_service import gerar_dados_demonstrativo_financeiro
from sme_ptrf_apps.core.services.demonstrativo_financeiro_pdf_service import gerar_arquivo_demonstrativo_financeiro_pdf
from django.contrib.auth import get_user_model
from datetime import datetime

from celery import shared_task

from sme_ptrf_apps.core.models import (
    AcaoAssociacao,
    ObservacaoConciliacao
)

logger = logging.getLogger(__name__)


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=333333,
    soft_time_limit=333333
)
def regerar_demonstrativo_financeiro_async(
    data_inicio,
    data_fim,
    username
):
    query = DemonstrativoFinanceiro.objects.filter(versao="FINAL").filter(
        criado_em__range=[data_inicio, data_fim]).order_by(
        'prestacao_conta__associacao__unidade__dre__nome',
        'prestacao_conta__associacao__unidade__nome',
    )

    logger.info(f"O processo irá ocorrer para: {query.count()} demonstrativos")

    usuario = get_user_model().objects.get(username=username)

    for demonstrativo in query:

        logger.info(f"Iniciando regeração do demonstrativo: id: {demonstrativo.id} - {demonstrativo}")

        demonstrativo.arquivo_pdf_substituido = demonstrativo.arquivo_pdf
        demonstrativo.arquivo_pdf_regerado = True

        acoes = demonstrativo.prestacao_conta.associacao.acoes.filter(status=AcaoAssociacao.STATUS_ATIVA)
        periodo = demonstrativo.prestacao_conta.periodo
        conta_associacao = demonstrativo.conta_associacao

        prestacao = demonstrativo.prestacao_conta
        previa = False

        try:
            observacao_conciliacao = ObservacaoConciliacao.objects.filter(
                periodo__uuid=periodo.uuid,
                conta_associacao__uuid=conta_associacao.uuid
            ).first()
        except Exception:
            observacao_conciliacao = None

        dados_demonstrativo = gerar_dados_demonstrativo_financeiro(
            usuario,
            acoes,
            periodo,
            conta_associacao,
            prestacao,
            observacao_conciliacao=observacao_conciliacao,
            previa=previa
        )

        data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        info_rodape = f"Documento final gerado pelo adminstrador do sistema, via SIG - Escola, em {data_geracao}"

        dados_demonstrativo["data_geracao_documento"] = info_rodape

        gerar_arquivo_demonstrativo_financeiro_pdf(dados_demonstrativo, demonstrativo)

        logger.info(f"Processo de regeração do demonstrativo: id: {demonstrativo.id} - {demonstrativo} finalizado")

    logger.info(f"Processo de regeração dos demonstrativos finalizado!")
