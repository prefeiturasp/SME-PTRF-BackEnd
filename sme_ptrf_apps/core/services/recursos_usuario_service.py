from sme_ptrf_apps.core.models import Recurso, Associacao, PeriodoInicialAssociacao


def recursos_disponiveis_usuario(user):
    # Se usuário tem acesso SME, retorna todos os recursos ativos
    if user.pode_acessar_sme or user.visoes.filter(nome='SME').exists():
        return Recurso.objects.filter(ativo=True).distinct().order_by('nome')

    # Obtém associações das unidades do usuário
    associacoes = Associacao.objects.filter(unidade__in=user.unidades.all())

    if not associacoes.exists():
        return Recurso.objects.none()

    periodo_inicial_associacao = PeriodoInicialAssociacao.objects.filter(
        associacao__in=associacoes
    )

    if not periodo_inicial_associacao.exists():
        return Recurso.objects.none()

    recurso_ids = periodo_inicial_associacao.values_list('recurso_id', flat=True)

    recursos = Recurso.objects.filter(
        id__in=recurso_ids,
        ativo=True,
    ).distinct().order_by('nome')

    return recursos
