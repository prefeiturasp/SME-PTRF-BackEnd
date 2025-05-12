from factory import DjangoModelFactory, SubFactory
from faker import Faker
from sme_ptrf_apps.paa.models import Paa
from sme_ptrf_apps.paa.fixtures.factories.periodo_paa import PeriodoPaaFactory
from sme_ptrf_apps.core.fixtures.factories.associacao_factory import AssociacaoFactory

fake = Faker("pt_BR")


class PaaFactory(DjangoModelFactory):
    class Meta:
        model = Paa

    periodo_paa = SubFactory(PeriodoPaaFactory)
    associacao = SubFactory(AssociacaoFactory)
