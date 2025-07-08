from django.db.models import Case, When, Value, IntegerField, F, CharField
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum


def queryset_prioridades_paa(qs):
    # Definição da ordenação customizada definida em história AB#127464
    PRIORIDADEPAA_ORDENACAO_PRIORIDADE_RECURSO = Case(
        # Prioridade Sim
        When(prioridade=True, recurso=RecursoOpcoesEnum.PTRF.name, then=Value(1)),
        When(prioridade=True, recurso=RecursoOpcoesEnum.PDDE.name, then=Value(2)),
        When(prioridade=True, recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name, then=Value(3)),

        # Prioridade Não
        When(prioridade=False, recurso=RecursoOpcoesEnum.PTRF.name, then=Value(4)),
        When(prioridade=False, recurso=RecursoOpcoesEnum.PDDE.name, then=Value(5)),
        When(prioridade=False, recurso=RecursoOpcoesEnum.RECURSO_PROPRIO.name, then=Value(6)),
        default=Value(99),
        output_field=IntegerField()
    )

    # Alfabética
    PRIORIDADEPAA_ORDENACAO_NOME = Case(
        When(recurso=RecursoOpcoesEnum.PTRF.name, then=F('acao_associacao__acao__nome')),
        When(recurso=RecursoOpcoesEnum.PDDE.name, then=F('acao_pdde__nome')),
        When(recurso=RecursoOpcoesEnum.RECURSO_PROPRIO, then=F('especificacao_material__descricao')),
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
    )

    return qs.annotate(ordem_customizada=PRIORIDADEPAA_ORDENACAO_PRIORIDADE_RECURSO) \
        .order_by('ordem_customizada', PRIORIDADEPAA_ORDENACAO_NOME)
