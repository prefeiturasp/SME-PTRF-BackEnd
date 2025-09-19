from sme_ptrf_apps.core.models import TipoAcertoDocumento, TipoAcertoLancamento


def tem_apenas_ajustes_externos(prestacao_conta):
    """
    Verifica se a prestação de contas tem APENAS ajustes externos (sem outras categorias de ajuste)
    
    Args:
        prestacao_conta: Instância de PrestacaoConta
        
    Returns:
        bool: True se tem apenas ajustes externos, False caso contrário
    """
    if not prestacao_conta:
        return False
    
    ultima_analise = prestacao_conta.analises_da_prestacao.last()
    if not ultima_analise:
        return False
    
    tem_ajustes_externos_documentos = ultima_analise.analises_de_documento.filter(
        solicitacoes_de_ajuste_da_analise__tipo_acerto__categoria=TipoAcertoDocumento.CATEGORIA_AJUSTES_EXTERNOS
    ).exists()
    
    tem_ajustes_externos_lancamentos = ultima_analise.analises_de_lancamentos.filter(
        solicitacoes_de_ajuste_da_analise__tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_AJUSTES_EXTERNOS
    ).exists()
    
    tem_ajustes_externos = tem_ajustes_externos_documentos or tem_ajustes_externos_lancamentos
    
    if not tem_ajustes_externos:
        return False
    
    tem_outros_ajustes_documentos = ultima_analise.analises_de_documento.filter(
        solicitacoes_de_ajuste_da_analise__tipo_acerto__categoria__in=[
            TipoAcertoDocumento.CATEGORIA_EDICAO_INFORMACAO,
            TipoAcertoDocumento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO,
            TipoAcertoDocumento.CATEGORIA_INCLUSAO_CREDITO,
            TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO
        ]
    ).exists()
    
    tem_outros_ajustes_lancamentos = ultima_analise.analises_de_lancamentos.filter(
        solicitacoes_de_ajuste_da_analise__tipo_acerto__categoria__in=[
            TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO,
            TipoAcertoLancamento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO,
            TipoAcertoLancamento.CATEGORIA_CONCILIACAO_LANCAMENTO,
            TipoAcertoLancamento.CATEGORIA_DESCONCILIACAO_LANCAMENTO,
            TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO,
            TipoAcertoLancamento.CATEGORIA_DEVOLUCAO
        ]
    ).exists()
    
    tem_outros_ajustes = tem_outros_ajustes_documentos or tem_outros_ajustes_lancamentos
    
    return tem_ajustes_externos and not tem_outros_ajustes
