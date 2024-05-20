import logging

from sme_ptrf_apps.core.models import RelacaoBens
from sme_ptrf_apps.despesas.models import RateioDespesa
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL

from ..services.relacao_bens_dados_service import (
    gerar_dados_relacao_de_bens,
    persistir_dados_relacao_bens,
    formatar_e_retornar_dados_relatorio_relacao_bens,
)
from ..services.relacao_bens_pdf_service import gerar_arquivo_relacao_de_bens_pdf

LOGGER = logging.getLogger(__name__)


def gerar_arquivo_relacao_de_bens_dados_persistidos(relacao_bens):
    relatorio_persistido = relacao_bens.relatoriorelacaobens_set.last()
    if relatorio_persistido:
        gerar_arquivo_relacao_de_bens_pdf(dados_relacao_de_bens=formatar_e_retornar_dados_relatorio_relacao_bens(relatorio_persistido),
                                        relacao_bens=relacao_bens)


def gerar_arquivo_relacao_de_bens(periodo, conta_associacao, usuario, prestacao=None, previa=False, criar_arquivos=True):
    rateios = RateioDespesa.rateios_da_conta_associacao_no_periodo(
        conta_associacao=conta_associacao,
        periodo=periodo,
        aplicacao_recurso=APLICACAO_CAPITAL,
        nao_exibir_em_rel_bens=False,
    )

    if rateios:
        relacao_bens, _ = RelacaoBens.objects.update_or_create(
            conta_associacao=conta_associacao,
            prestacao_conta=prestacao,
            periodo_previa=None if prestacao else periodo,
            versao=RelacaoBens.VERSAO_PREVIA if previa else RelacaoBens.VERSAO_FINAL,
            status=RelacaoBens.STATUS_EM_PROCESSAMENTO,
        )
        # PDF
        dados_relacao_de_bens = gerar_dados_relacao_de_bens(conta_associacao=conta_associacao, periodo=periodo, rateios=rateios, usuario=usuario, previa=previa)

        if criar_arquivos:
            # gerar_arquivo_relacao_de_bens_pdf(dados_relacao_de_bens=formatar_e_retornar_dados_relatorio_relacao_bens(relatorio_persistido), relacao_bens=relacao_bens)
            gerar_arquivo_relacao_de_bens_pdf(dados_relacao_de_bens=dados_relacao_de_bens, relacao_bens=relacao_bens)

        relacao_bens.arquivo_concluido()


def apagar_previas_relacao_de_bens(periodo, conta_associacao):
    for relacao_bens in RelacaoBens.objects.filter(periodo_previa=periodo, conta_associacao=conta_associacao):
        for relatorio in relacao_bens.relatoriorelacaobens_set.all():
            for item_relatorio in relatorio.bens.all():
                item_relatorio.delete()
            relatorio.delete()
        relacao_bens.delete()


def _retornar_dados_relatorio_relacao_de_bens(relacao_bens):
    relatorio_persistido = relacao_bens.relatoriorelacaobens_set.last()
    if relatorio_persistido:
        return formatar_e_retornar_dados_relatorio_relacao_bens(relatorio_persistido)
    return None


def _persistir_arquivo_relacao_de_bens(periodo, conta_associacao, usuario, prestacao=None, previa=False):
    rateios = RateioDespesa.rateios_da_conta_associacao_no_periodo(
        conta_associacao=conta_associacao,
        periodo=periodo,
        aplicacao_recurso=APLICACAO_CAPITAL,
        nao_exibir_em_rel_bens=False,
    )

    if rateios:
        relacao_bens, _ = RelacaoBens.objects.update_or_create(
            conta_associacao=conta_associacao,
            prestacao_conta=prestacao,
            periodo_previa=None if prestacao else periodo,
            versao=RelacaoBens.VERSAO_PREVIA if previa else RelacaoBens.VERSAO_FINAL,
            status=RelacaoBens.STATUS_A_PROCESSAR,
        )

        LOGGER.info(f'Relacão de bens criada/atualizada com sucesso {relacao_bens}.')

        LOGGER.info(f'Iniciando persistir_dados_relacao_bens {relacao_bens}.')

        persistir_dados_relacao_bens(
            conta_associacao=conta_associacao,
            periodo=periodo,
            rateios=rateios,
            relacao_bens=relacao_bens,
            usuario=usuario
        )

        return relacao_bens
    else:
        LOGGER.info("Não houve bem adquirido ou produzido no referido período (%s).", str(periodo))
    return None
