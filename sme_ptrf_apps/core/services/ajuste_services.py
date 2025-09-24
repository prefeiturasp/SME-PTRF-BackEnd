from sme_ptrf_apps.core.models import TipoAcertoDocumento, TipoAcertoLancamento


def possui_apenas_categorias_que_nao_requerem_ata(prestacao_conta):
    """
    Retorna True quando a prestação possui SOMENTE categorias que não
    geram ata de retificação (AJUSTES_EXTERNOS e SOLICITACAO_ESCLARECIMENTO)
    e não possui nenhuma outra categoria.
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

    tem_solic_esclarecimento_documentos = ultima_analise.analises_de_documento.filter(
        solicitacoes_de_ajuste_da_analise__tipo_acerto__categoria=TipoAcertoDocumento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO
    ).exists()
    tem_solic_esclarecimento_lancamentos = ultima_analise.analises_de_lancamentos.filter(
        solicitacoes_de_ajuste_da_analise__tipo_acerto__categoria=TipoAcertoLancamento.CATEGORIA_SOLICITACAO_ESCLARECIMENTO
    ).exists()

    tem_alguma_nao_gera_ata = (
        tem_ajustes_externos_documentos or tem_ajustes_externos_lancamentos or
        tem_solic_esclarecimento_documentos or tem_solic_esclarecimento_lancamentos
    )

    if not tem_alguma_nao_gera_ata:
        return False

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

    tem_outros_documentos = ultima_analise.analises_de_documento.filter(
        solicitacoes_de_ajuste_da_analise__tipo_acerto__categoria__in=categorias_documento_que_geram_ata
    ).exists()
    tem_outros_lancamentos = ultima_analise.analises_de_lancamentos.filter(
        solicitacoes_de_ajuste_da_analise__tipo_acerto__categoria__in=categorias_lancamento_que_geram_ata
    ).exists()

    return not (tem_outros_documentos or tem_outros_lancamentos)
