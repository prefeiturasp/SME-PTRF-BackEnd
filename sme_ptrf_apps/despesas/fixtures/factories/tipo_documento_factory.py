from factory import Sequence
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.despesas.models.tipo_documento import TipoDocumento

fake = Faker("pt_BR")


class TipoDocumentoFactory(DjangoModelFactory):
    class Meta:
        model = TipoDocumento

    nome = Sequence(lambda n: fake.unique.name())
