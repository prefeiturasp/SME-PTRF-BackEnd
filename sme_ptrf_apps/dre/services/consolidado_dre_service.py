import logging
from django.db.models import Q
from ..models import ConsolidadoDRE
from ..tasks import concluir_consolidado_dre_async
from ...core.models import Unidade, PrestacaoConta

logger = logging.getLogger(__name__)


def retornar_trilha_de_status(dre_uuid=None, periodo_uuid=None, add_aprovado_ressalva=False,
                              add_info_devolvidas_retornadas=False):
    """
    :param add_aprovado_ressalva: True para retornar a quantidade de aprovados com ressalva separadamente ou
    False para retornar a quantidade de aprovadas com ressalva somada a quantidade de aprovadas

    :param add_info_devolvidas_retornadas: True para retornar a quantidade de devolvidas retornadas no card de
    devolução.
    """

    """
    Destaque ou não destaque do status
        0 - Simples: Circulo preenchido verde
        1 - Duplo: Circulo preenchido verde e borda verde
        2 - Vermelho: Circulo preenchido vermelho
    """

    from ...core.models import Associacao, PrestacaoConta

    titulo_e_estilo_css = {
        'NAO_RECEBIDA':
            {
                'titulo': 'Não recebido',
                'estilo_css': 2
            },
        'RECEBIDA':
            {
                'titulo': 'Recebida e<br/>aguardando análise',
                'estilo_css': 1
            },
        'DEVOLVIDA':
            {
                'titulo': 'Devolvido<br/>para acertos',
                'estilo_css': 1
            },
        'EM_ANALISE':
            {
                'titulo': 'Em análise',
                'estilo_css': 1
            },
        'CONCLUIDO':
            {
                'titulo': 'Concluído e<br/>aguardando publicação',
                'estilo_css': 0
            },
        'PUBLICADO':
            {
                'titulo': 'Publicado',
                'estilo_css': 0
            },
        'APROVADA':
            {
                'titulo': 'Aprovado',
                'estilo_css': 1
            },
        'REPROVADA':
            {
                'titulo': 'Reprovado',
                'estilo_css': 1
            },

    }

    if add_aprovado_ressalva:
        titulo_e_estilo_css['APROVADA_RESSALVA']['titulo'] = "Aprovadas com ressalvas"
        titulo_e_estilo_css['APROVADA_RESSALVA']['estilo_css'] = 1

    cards = []
    qs = PrestacaoConta.objects.filter(periodo__uuid=periodo_uuid, associacao__unidade__dre__uuid=dre_uuid)

    quantidade_pcs_apresentadas = 0
    for status, itens in titulo_e_estilo_css.items():
        if status == 'NAO_RECEBIDA':
            continue

        quantidade_status = qs.filter(status=status).count()

        if status == 'APROVADA' and not add_aprovado_ressalva:
            quantidade_status += qs.filter(status='APROVADA_RESSALVA').count()

        if status == 'DEVOLVIDA':
            quantidade_status += qs.filter(status__in=['DEVOLVIDA_RETORNADA', 'DEVOLVIDA_RECEBIDA']).count()

        quantidade_pcs_apresentadas += quantidade_status

        if status == 'DEVOLVIDA' and add_info_devolvidas_retornadas:
            quantidade_retornadas = qs.filter(status='DEVOLVIDA_RETORNADA').count()
            card = {
                "titulo": itens['titulo'],
                "estilo_css": itens['estilo_css'],
                "quantidade_prestacoes": quantidade_status,
                "quantidade_retornadas": quantidade_retornadas,
                "status": status
            }
            cards.append(card)
        elif not status == 'PUBLICADO' and not status == 'CONCLUIDO':
            card = {
                "titulo": itens['titulo'],
                "estilo_css": itens['estilo_css'],
                "quantidade_prestacoes": quantidade_status,
                "status": status
            }
            cards.append(card)

        if status == 'PUBLICADO':
            quantidade_pcs_publicadas = qs.filter(publicada=True).count()
            card_publicadas = {
                "titulo":  itens['titulo'],
                "estilo_css":  itens['estilo_css'],
                "quantidade_prestacoes": quantidade_pcs_publicadas,
                "status": 'PUBLICADO'
            }
            cards.append(card_publicadas)

        if status == 'CONCLUIDO':
            quantidade_pcs_concluidas = qs.filter(
                (Q(status='APROVADA') | Q(status='APROVADA_RESSALVA') | Q(status='REPROVADA')) &
                Q(publicada=False)
            ).count()
            card_concluidas = {
                "titulo":  itens['titulo'],
                "estilo_css":  itens['estilo_css'],
                "quantidade_prestacoes": quantidade_pcs_concluidas,
                "status": 'CONCLUIDO'
            }
            cards.append(card_concluidas)

    quantidade_unidades_dre = Associacao.objects.filter(unidade__dre__uuid=dre_uuid).exclude(cnpj__exact='').count()
    quantidade_pcs_nao_apresentadas = quantidade_unidades_dre - quantidade_pcs_apresentadas
    card_nao_recebidas = {
        "titulo": titulo_e_estilo_css['NAO_RECEBIDA']['titulo'],
        "estilo_css": titulo_e_estilo_css['NAO_RECEBIDA']['estilo_css'],
        "quantidade_prestacoes": quantidade_pcs_nao_apresentadas,
        "quantidade_nao_recebida": qs.filter(status='NAO_RECEBIDA').count(),
        "status": 'NAO_RECEBIDA'
    }

    cards.insert(0, card_nao_recebidas)

    return cards


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


def concluir_consolidado_dre(dre, periodo, parcial, usuario, ata):
    consolidado_dre = ConsolidadoDRE.criar(dre=dre, periodo=periodo)
    logger.info(f'Criado Consolidado DRE  {consolidado_dre}.')

    consolidado_dre.passar_para_status_em_processamento()
    logger.info(f'Consolidado DRE em processamento - {consolidado_dre}.')

    dre_uuid = dre.uuid
    periodo_uuid = periodo.uuid
    consolidado_dre_uuid = consolidado_dre.uuid
    ata_uuid = ata.uuid

    concluir_consolidado_dre_async.delay(
        dre_uuid=dre_uuid,
        periodo_uuid=periodo_uuid,
        parcial=parcial,
        usuario=usuario,
        consolidado_dre_uuid=consolidado_dre_uuid,
        ata_uuid=ata_uuid,
    )

    return consolidado_dre
