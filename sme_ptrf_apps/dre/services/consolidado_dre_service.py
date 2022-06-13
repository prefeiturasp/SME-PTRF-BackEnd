import logging
from django.db.models import Q
from ..models import ConsolidadoDRE
from ..tasks import concluir_consolidado_dre_async
from ...core.models import Unidade, PrestacaoConta

logger = logging.getLogger(__name__)


def status_consolidado_dre(dre, periodo):
    """
    Calcula o status Consolidado da DRE em determinado período:

    PCs em análise?	Relatório gerado?	Texto status	                                                                            Cor
    Sim	            Não	                Ainda constam prestações de contas das associações em análise. Relatório não gerado.	    0
    Sim	            Sim (parcial)	    Ainda constam prestações de contas das associações em análise. Relatório parcial gerado.	1
    Não	            Não	                Análise de prestações de contas das associações completa. Relatório não gerado.	            2
    Não	            Sim (parcial)	    Análise de prestações de contas das associações completa. Relatório parcial gerado.	        2
    Não	            Sim (final)	        Análise de prestações de contas das associações completa. Relatório final gerado.	        3
    """

    LEGENDA_COR = {
        'NAO_GERADOS': {'com_pcs_em_analise': 0, 'sem_pcs_em_analise': 2},
        'GERADOS_PARCIAIS': {'com_pcs_em_analise': 1, 'sem_pcs_em_analise': 2},
        'GERADOS_TOTAIS': {'com_pcs_em_analise': 0, 'sem_pcs_em_analise': 3},
        'EM_PROCESSAMENTO': {'com_pcs_em_analise': 0, 'sem_pcs_em_analise': 3},
    }

    pcs_em_analise = PrestacaoConta.objects.filter(periodo=periodo,
                                                   status__in=['EM_ANALISE', 'RECEBIDA', 'NAO_RECEBIDA', 'DEVOLVIDA'],
                                                   associacao__unidade__dre=dre).exists()

    consolidado_dre = ConsolidadoDRE.objects.filter(dre=dre, periodo=periodo).first()

    status_consolidado_dre = consolidado_dre.status if consolidado_dre else 'NAO_GERADOS'

    status_txt_consolidado_dre = f'{ConsolidadoDRE.STATUS_NOMES[status_consolidado_dre]}.'

    if pcs_em_analise:
        status_txt_analise = 'Ainda constam prestações de contas das associações em análise.'
    else:
        status_txt_analise = 'Análise de prestações de contas das associações completa.'

    status_txt_geracao = f'{status_txt_analise} {status_txt_consolidado_dre}'

    cor_idx = LEGENDA_COR[status_consolidado_dre]['com_pcs_em_analise' if pcs_em_analise else 'sem_pcs_em_analise']

    status = {
        'pcs_em_analise': pcs_em_analise,
        'status_geracao': status_consolidado_dre,
        'status_txt': status_txt_geracao,
        'cor_idx': cor_idx,
        'status_arquivo': 'Documento pendente de geração' if status_consolidado_dre == 'NAO_GERADO' else consolidado_dre.__str__(),
    }
    return status


def verificar_se_status_parcial_ou_total(dre_uuid, periodo_uuid):
    dre = Unidade.dres.get(uuid=dre_uuid)
    prestacoes = PrestacaoConta.objects.filter(periodo__uuid=periodo_uuid, associacao__unidade__dre__uuid=dre.uuid)
    qtde_prestacoes = prestacoes.filter(Q(status='RECEBIDA') | Q(status='DEVOLVIDA') | Q(status='EM_ANALISE')).count()
    return qtde_prestacoes > 0


def concluir_consolidado_dre(dre, periodo, parcial, usuario):

    consolidado_dre = ConsolidadoDRE.criar(dre=dre, periodo=periodo)
    logger.info(f'Criado Consolidado DRE  {consolidado_dre}.')

    consolidado_dre.passar_para_status_em_processamento()
    logger.info(f'Consolidado DRE em processamento - {consolidado_dre}.')

    dre_uuid = dre.uuid
    periodo_uuid = periodo.uuid
    consolidado_dre_uuid = consolidado_dre.uuid

    concluir_consolidado_dre_async.delay(
        dre_uuid=dre_uuid,
        periodo_uuid=periodo_uuid,
        parcial=parcial,
        usuario=usuario,
        consolidado_dre_uuid=consolidado_dre_uuid,
    )

    return consolidado_dre








