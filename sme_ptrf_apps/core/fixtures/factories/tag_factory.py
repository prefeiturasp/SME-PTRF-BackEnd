from factory import Sequence, LazyFunction
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.models import Recurso, Tag
from sme_ptrf_apps.core.choices import StatusTag

fake = Faker("pt_BR")


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag

    nome = Sequence(lambda n: f"{fake.word()}_{n:06d}")
    status = LazyFunction(lambda: StatusTag.ATIVO)
    recurso = LazyFunction(lambda: Recurso.objects.get(legado=True))
