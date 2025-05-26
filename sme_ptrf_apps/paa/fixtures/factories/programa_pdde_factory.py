from factory import DjangoModelFactory, Sequence
from faker import Faker
from sme_ptrf_apps.paa.models.programa_pdde import ProgramaPdde

fake = Faker("pt_BR")


class ProgramaPddeFactory(DjangoModelFactory):
    class Meta:
        model = ProgramaPdde

    nome = Sequence(lambda n: fake.unique.name())
