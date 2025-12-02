from factory import Sequence
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.paa.models import OutroRecurso

fake = Faker("pt_BR")


class OutroRecursoFactory(DjangoModelFactory):
    class Meta:
        model = OutroRecurso

    nome = Sequence(lambda n: fake.unique.name())
