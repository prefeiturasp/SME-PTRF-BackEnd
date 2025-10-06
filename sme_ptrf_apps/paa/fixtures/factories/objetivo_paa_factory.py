from factory import SubFactory, Sequence, LazyFunction
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models import ObjetivoPaa
from sme_ptrf_apps.paa.fixtures.factories import PaaFactory
from sme_ptrf_apps.paa.models.objetivo_paa import StatusChoices

fake = Faker("pt_BR")


class ObjetivoPaaFactory(DjangoModelFactory):
    class Meta:
        model = ObjetivoPaa

    paa = SubFactory(PaaFactory)
    status = LazyFunction(lambda: fake.random_element([StatusChoices.ATIVO, StatusChoices.INATIVO]))
    nome = Sequence(lambda n: fake.unique.word())
