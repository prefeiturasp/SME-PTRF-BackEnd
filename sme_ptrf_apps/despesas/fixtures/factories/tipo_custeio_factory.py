from factory import DjangoModelFactory, Sequence
from faker import Faker
from sme_ptrf_apps.despesas.models.tipo_custeio import TipoCusteio

fake = Faker("pt_BR")

class TipoCusteioFactory(DjangoModelFactory):
    class Meta:
        model = TipoCusteio

    nome = Sequence(lambda n: fake.unique.name())
