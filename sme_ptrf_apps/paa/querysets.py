from django.db.models import Case, When, Value, IntegerField, F, CharField
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum


def queryset_prioridades_paa(qs):
    # Definição da ordenação customizada definida em história AB#127464
    PRIORIDADEPAA_ORDENACAO_PRIORIDADE_RECURSO = Case(
        # Prioridade Sim Sem Valor - Para os casos de duplicidades, aparecerem no topo da tabela
        When(valor_total__isnull=True, prioridade=True, recurso=RecursoOpcoesEnum.PTRF.name, then=Value(1)),
        When(valor_total__isnull=True, prioridade=True, recurso=RecursoOpcoesEnum.PDDE.name, then=Value(2)),
        When(valor_total__isnull=True, prioridade=True, recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name, then=Value(3)),
        When(valor_total__isnull=True, prioridade=True, recurso=RecursoOpcoesEnum.OUTRO_RECURSO.name, then=Value(4)),

        # Prioridade Não Sem Valor - Para os casos de duplicidades, aparecerem no topo da tabela
        When(valor_total__isnull=True, prioridade=False, recurso=RecursoOpcoesEnum.PTRF.name, then=Value(5)),
        When(valor_total__isnull=True, prioridade=False, recurso=RecursoOpcoesEnum.PDDE.name, then=Value(6)),
        When(valor_total__isnull=True, prioridade=False, recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name, then=Value(7)),
        When(valor_total__isnull=True, prioridade=False, recurso=RecursoOpcoesEnum.OUTRO_RECURSO.name, then=Value(8)),

        # Prioridade Sim
        When(prioridade=True, recurso=RecursoOpcoesEnum.PTRF.name, then=Value(9)),
        When(prioridade=True, recurso=RecursoOpcoesEnum.PDDE.name, then=Value(10)),
        When(prioridade=True, recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name, then=Value(11)),
        When(prioridade=True, recurso=RecursoOpcoesEnum.OUTRO_RECURSO.name, then=Value(12)),

        # Prioridade Não
        When(prioridade=False, recurso=RecursoOpcoesEnum.PTRF.name, then=Value(13)),
        When(prioridade=False, recurso=RecursoOpcoesEnum.PDDE.name, then=Value(14)),
        When(prioridade=False, recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name, then=Value(15)),
        When(prioridade=False, recurso=RecursoOpcoesEnum.OUTRO_RECURSO.name, then=Value(16)),
        default=Value(99),
        output_field=IntegerField(),
    )

    # Alfabética
    PRIORIDADEPAA_ORDENACAO_NOME = Case(
        When(recurso=RecursoOpcoesEnum.PTRF.name, then=F('acao_associacao__acao__nome')),
        When(recurso=RecursoOpcoesEnum.PDDE.name, then=F('acao_pdde__nome')),
        When(recurso=RecursoOpcoesEnum.RECURSO_PROPRIO, then=F('especificacao_material__descricao')),
        When(recurso=RecursoOpcoesEnum.OUTRO_RECURSO.name, then=F('outro_recurso__nome')),
        default=Value(''),
        output_field=CharField()
    )

    qs = qs.select_related(
        'paa',
        'acao_associacao',
        'acao_associacao__acao',
        'acao_associacao__associacao',
        'programa_pdde',
        'acao_pdde__programa',
        'especificacao_material',
        'especificacao_material__tipo_custeio',
        'tipo_despesa_custeio',
        'outro_recurso'
    )

    return qs.annotate(ordem_customizada=PRIORIDADEPAA_ORDENACAO_PRIORIDADE_RECURSO) \
        .order_by(
            'ordem_customizada',
            PRIORIDADEPAA_ORDENACAO_NOME,
            'tipo_aplicacao',
            'tipo_despesa_custeio__nome',
            'especificacao_material__descricao')
