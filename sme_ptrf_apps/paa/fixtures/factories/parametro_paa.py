from factory import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models import ParametroPaa

fake = Faker("pt_BR")


class ParametroPaaFactory(DjangoModelFactory):
    class Meta:
        model = ParametroPaa

    mes_elaboracao_paa = fake.unique.random_int(min=1, max=12)
