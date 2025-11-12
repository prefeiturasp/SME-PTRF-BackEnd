from factory import SubFactory, LazyFunction
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models import AtividadeEstatutariaPaa
from sme_ptrf_apps.paa.fixtures.factories import PaaFactory, AtividadeEstatutariaFactory

fake = Faker("pt_BR")


class AtividadeEstatutariaPaaFactory(DjangoModelFactory):
    class Meta:
        model = AtividadeEstatutariaPaa

    paa = SubFactory(PaaFactory)
    atividade_estatutaria = SubFactory(AtividadeEstatutariaFactory)
    data = LazyFunction(lambda: fake.date_between(start_date="-2y", end_date="today"))
