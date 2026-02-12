from django.core.exceptions import ValidationError


def validar_troca_recurso(acao, recurso_novo):
    if not acao.pk:
        return

    if acao.recurso_id == recurso_novo.id:
        return

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

    if not any(verificacoes):
        raise ValidationError(
            "Não é possível alterar o recurso de uma ação já utilizada."
        )
