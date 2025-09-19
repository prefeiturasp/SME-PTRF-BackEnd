from sme_ptrf_apps.core.models.tipo_acerto_documento import TipoAcertoDocumento
from faker import Faker
from factory import Sequence, LazyAttribute
from factory.django import DjangoModelFactory

fake = Faker("pt_BR")


class TipoAcertoDocumentoFactory(DjangoModelFactory):
    class Meta:
        model = TipoAcertoDocumento

    nome = Sequence(lambda n: f"Tipo Acerto {n}")
    categoria = LazyAttribute(lambda x: fake.random_element(
        elements=[choice[0] for choice in TipoAcertoDocumento.CATEGORIA_CHOICES]))
