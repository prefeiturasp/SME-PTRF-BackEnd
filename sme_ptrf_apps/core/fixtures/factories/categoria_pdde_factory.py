from factory import DjangoModelFactory, Sequence
from faker import Faker
from sme_ptrf_apps.core.models.categoria_pdde import CategoriaPdde

fake = Faker("pt_BR")


class CategoriaPddeFactory(DjangoModelFactory):
    class Meta:
        model = CategoriaPdde

    nome = Sequence(lambda n: fake.unique.name())
