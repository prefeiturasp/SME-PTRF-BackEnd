from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.fixtures.factories.acao_associacao_factory import AcaoAssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.fixtures.factories.periodo_factory import PeriodoFactory
from sme_ptrf_apps.core.fixtures.factories.prestacao_conta_factory import PrestacaoContaFactory
from sme_ptrf_apps.core.models.fechamento_periodo import FechamentoPeriodo


fake = Faker()


class FechamentoPeriodoFactory(DjangoModelFactory):
    class Meta:
        model = FechamentoPeriodo

    prestacao_conta = SubFactory(PrestacaoContaFactory)
    periodo = SubFactory(PeriodoFactory)
    associacao = SubFactory(AssociacaoFactory)
    acao_associacao = SubFactory(AcaoAssociacaoFactory)

    # TODO adicionar outros campos
