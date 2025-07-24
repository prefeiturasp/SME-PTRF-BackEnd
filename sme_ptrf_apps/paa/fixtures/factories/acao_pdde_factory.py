from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models import AcaoPdde
from sme_ptrf_apps.paa.fixtures.factories.programa_pdde_factory import ProgramaPddeFactory

fake = Faker("pt_BR")


class AcaoPddeFactory(DjangoModelFactory):
    class Meta:
        model = AcaoPdde

    nome = Sequence(lambda n: fake.unique.name())
    programa = SubFactory(ProgramaPddeFactory)
