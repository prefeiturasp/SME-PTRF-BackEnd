def checa_se_pode_alterar_recurso(acao):
    if not acao.pk:
        return True

    verificacoes = [
        acao.associacoes_da_acao.exists(),
        acao.associacoes_da_acao.filter(rateios_da_associacao__isnull=False).exists(),
        acao.associacoes_da_acao.filter(fechamentos_da_acao__isnull=False).exists(),
        acao.associacoes_da_acao.filter(receitas_da_associacao__isnull=False).exists(),
        acao.associacoes_da_acao.filter(valores_reprogramados_da_acao__isnull=False).exists(),
        acao.associacoes_da_acao.filter(prioridade_paa_da_associacao__isnull=False).exists(),
        acao.associacoes_da_acao.filter(receita_prevista_paa_da_associacao__isnull=False).exists(),
        acao.associacoes_da_acao.filter(repasses_da_associacao__isnull=False).exists()
    ]

    # se pelo menos algum item de verificacoes existir, retorna True
    return not any(verificacoes)
