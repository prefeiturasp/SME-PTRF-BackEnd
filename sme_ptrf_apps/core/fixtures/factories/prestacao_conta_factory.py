from factory import DjangoModelFactory, SubFactory
from faker import Faker
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from .periodo_factory import PeriodoFactory
fake = Faker("pt_BR")

class PrestacaoContaFactory(DjangoModelFactory):
    class Meta:
        model = PrestacaoConta

    periodo = SubFactory(PeriodoFactory)
    associacao = SubFactory(AssociacaoFactory)
