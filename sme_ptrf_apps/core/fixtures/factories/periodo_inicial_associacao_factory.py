from factory import SubFactory
from factory.django import DjangoModelFactory
from sme_ptrf_apps.core.models.periodo_inicial_associacao import PeriodoInicialAssociacao
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.periodo_factory import PeriodoFactory


class PeriodoInicialAssociacaoFactory(DjangoModelFactory):
    class Meta:
        model = PeriodoInicialAssociacao

    periodo_inicial = SubFactory(PeriodoFactory)
    associacao = SubFactory(AssociacaoFactory)
