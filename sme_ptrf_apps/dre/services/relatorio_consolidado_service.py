import logging

from sme_ptrf_apps.core.models import PrestacaoConta
from sme_ptrf_apps.dre.models import RelatorioConsolidadoDRE

logger = logging.getLogger(__name__)

def status_de_geracao_do_relatorio(dre, periodo, tipo_conta):
    '''
    Calcula o status de geração do relatório da DRE em determinado período e tipo de conta conforme tabela:

    PCs em análise?	Relatório gerado?	Texto status	                                                                            Cor
    Sim	            Não	                Ainda constam prestações de contas das associações em análise. Relatório não gerado.	    0
    Sim	            Sim (parcial)	    Ainda constam prestações de contas das associações em análise. Relatório parcial gerado.	1
    Não	            Não	                Análise de prestações de contas das associações completa. Relatório não gerado.	            2
    Não	            Sim (parcial)	    Análise de prestações de contas das associações completa. Relatório parcial gerado.	        2
    Não	            Sim (final)	        Análise de prestações de contas das associações completa. Relatório final gerado.	        3
    '''
    LEGENDA_COR = {
        'NAO_GERADO': {'com_pcs_em_analise': 0, 'sem_pcs_em_analise': 2},
        'GERADO_PARCIAL': {'com_pcs_em_analise': 1, 'sem_pcs_em_analise': 2},
        'GERADO_TOTAL': {'com_pcs_em_analise': 0, 'sem_pcs_em_analise': 3},
    }

    pcs_em_analise = PrestacaoConta.objects.filter(periodo=periodo,
                                                   status__in=['EM_ANALISE', 'RECEBIDA', 'NAO_RECEBIDA', 'DEVOLVIDA'],
                                                   associacao__unidade__dre=dre).exists()

    relatorio = RelatorioConsolidadoDRE.objects.filter(dre=dre, periodo=periodo, tipo_conta=tipo_conta).first()

    status_relatorio = relatorio.status if relatorio else 'NAO_GERADO'

    status_txt_relatorio = f'{RelatorioConsolidadoDRE.STATUS_NOMES[status_relatorio]}.'

    if pcs_em_analise:
        status_txt_analise = 'Ainda constam prestações de contas das associações em análise.'
    else:
        status_txt_analise = 'Análise de prestações de contas das associações completa.'


    status_txt_geracao = f'{status_txt_analise} {status_txt_relatorio}'

    cor_idx = LEGENDA_COR[status_relatorio]['com_pcs_em_analise' if pcs_em_analise else 'sem_pcs_em_analise']

    status = {
        'pcs_em_analise': pcs_em_analise,
        'status_geracao': status_relatorio,
        'status_txt': status_txt_geracao,
        'cor_idx': cor_idx,
    }
    return status


def informacoes_execucao_financeira(dre, periodo, tipo_conta):
    #TODO Implementar informacoes_execucao_financeira
    # Informações sumarizadas devem considerar apenas Prestações de Conta concluídas
    info = {
        'saldo_reprogramado_periodo_anterior_custeio': 0,
        'saldo_reprogramado_periodo_anterior_capital': 0,
        'saldo_reprogramado_periodo_anterior_livre': 0,
        'saldo_reprogramado_periodo_anterior_total': 0,

        'repasses_previstos_sme_custeio': 0,
        'repasses_previstos_sme_capital': 0,
        'repasses_previstos_sme_livre': 0,
        'repasses_previstos_sme_total': 0,

        'repasses_no_periodo_custeio': 0,
        'repasses_no_periodo_capital': 0,
        'repasses_no_periodo_livre': 0,
        'repasses_no_periodo_total': 0,

        'receitas_rendimento_no_periodo_custeio': 0,
        'receitas_rendimento_no_periodo_capital': 0,
        'receitas_rendimento_no_periodo_livre': 0,
        'receitas_rendimento_no_periodo_total': 0,

        'receitas_devolucao_no_periodo_custeio': 0,
        'receitas_devolucao_no_periodo_capital': 0,
        'receitas_devolucao_no_periodo_livre': 0,
        'receitas_devolucao_no_periodo_total': 0,

        'demais_creditos_no_periodo_custeio': 0,
        'demais_creditos_no_periodo_capital': 0,
        'demais_creditos_no_periodo_livre': 0,
        'demais_creditos_no_periodo_total': 0,

        'receitas_totais_no_periodo_custeio': 0,
        'receitas_totais_no_periodo_capital': 0,
        'receitas_totais_no_periodo_livre': 0,
        'receitas_totais_no_periodo_total': 0,

        'despesas_no_periodo_custeio': 0,
        'despesas_no_periodo_capital': 0,
        'despesas_no_periodo_total': 0,

        'saldo_reprogramado_proximo_periodo_custeio': 0,
        'saldo_reprogramado_proximo_periodo_capital': 0,
        'saldo_reprogramado_proximo_periodo_livre': 0,
        'saldo_reprogramado_proximo_periodo_total': 0,

        'devolucoes_ao_tesouro_no_periodo_total': 0,
    }

    return info



def informacoes_devolucoes_a_conta_ptrf(dre, periodo, tipo_conta):
    #TODO Implementar informacoes_devolucoes_a_conta_ptrf
    info = [
        {'tipo': 'Devolução à conta tipo 1', 'ocorrencias': 999, 'valor': 3000.00},
        {'tipo': 'Devolução à conta tipo 2', 'ocorrencias': 100, 'valor': 2000.00},
        {'tipo': 'Devolução à conta tipo 3', 'ocorrencias': 200, 'valor': 1000.00},
    ]

    return info


def informacoes_devolucoes_ao_tesouro(dre, periodo, tipo_conta):
    #TODO Implementar informacoes_devolucoes_ao_tesouro
    info = [
        {'tipo': 'Devolução ao tesouro tipo 1', 'ocorrencias': 999, 'valor': 3000.00},
        {'tipo': 'Devolução ao tesouro tipo 2', 'ocorrencias': 100, 'valor': 2000.00},
        {'tipo': 'Devolução ao tesouro tipo 3', 'ocorrencias': 200, 'valor': 1000.00},
    ]

    return info
