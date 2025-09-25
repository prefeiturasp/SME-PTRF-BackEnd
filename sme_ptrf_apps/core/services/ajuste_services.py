from sme_ptrf_apps.core.models import TipoAcertoDocumento, TipoAcertoLancamento



def possui_apenas_categorias_que_nao_requerem_ata(prestacao_conta):
    """
    Verifica se a prestação de contas possui apenas categorias que não requerem
    geração de ata de retificação.
    
    A função retorna True quando:
    - Não há acertos
    - Há apenas ajustes externos ou solicitações de esclarecimento
    - Há acertos que normalmente gerariam ata, mas não foram realizados
    
    A função retorna False quando:
    - Há acertos de categorias que geram ata e foram realizados
    
    Args:
        prestacao_conta: Instância de PrestacaoConta
        
    Returns:
        bool: True se não requer ata de retificação, False caso contrário
    """
    if not prestacao_conta:
        return False

    ultima_analise = prestacao_conta.analises_da_prestacao.filter(status='DEVOLVIDA').last()
    if not ultima_analise:
        return False

    if _tem_acertos_realizados_que_geram_ata(ultima_analise):
        return False

    return True


def _tem_acertos_realizados_que_geram_ata(ultima_analise):
    """
    Verifica se há acertos realizados de categorias que geram ata de retificação.
    
    Args:
        ultima_analise: Instância de AnalisePrestacaoConta
        
    Returns:
        bool: True se há acertos realizados que geram ata
    """
    categorias_documento_que_geram_ata = [
        TipoAcertoDocumento.CATEGORIA_EDICAO_INFORMACAO,
        TipoAcertoDocumento.CATEGORIA_INCLUSAO_CREDITO,
        TipoAcertoDocumento.CATEGORIA_INCLUSAO_GASTO,
    ]
    
    categorias_lancamento_que_geram_ata = [
        TipoAcertoLancamento.CATEGORIA_EDICAO_LANCAMENTO,
        TipoAcertoLancamento.CATEGORIA_EXCLUSAO_LANCAMENTO,
        TipoAcertoLancamento.CATEGORIA_CONCILIACAO_LANCAMENTO,
        TipoAcertoLancamento.CATEGORIA_DESCONCILIACAO_LANCAMENTO,
        TipoAcertoLancamento.CATEGORIA_DEVOLUCAO,
    ]

    if _tem_solicitacoes_realizadas_por_categoria(
        ultima_analise.analises_de_documento, 
        categorias_documento_que_geram_ata
    ):
        return True

    if _tem_solicitacoes_realizadas_por_categoria(
        ultima_analise.analises_de_lancamentos, 
        categorias_lancamento_que_geram_ata
    ):
        return True

    return False


def _tem_solicitacoes_realizadas_por_categoria(analises_queryset, categorias):
    """
    Verifica se há solicitações realizadas para as categorias especificadas.
    
    Args:
        analises_queryset: QuerySet de análises (documento ou lançamento)
        categorias: Lista de categorias a verificar
        
    Returns:
        bool: True se há solicitações realizadas para as categorias
    """
    analises_com_categorias = analises_queryset.filter(
        solicitacoes_de_ajuste_da_analise__tipo_acerto__categoria__in=categorias
    )
    
    for analise in analises_com_categorias:
        solicitacoes_realizadas = analise.solicitacoes_de_ajuste_da_analise.filter(
            tipo_acerto__categoria__in=categorias,
            status_realizacao='REALIZADO'
        )
        if solicitacoes_realizadas.exists():
            return True
    
    return False