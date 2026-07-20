from sme_ptrf_apps.core.models.tipo_acerto_documento import TipoAcertoDocumento
from faker import Faker
from factory import Sequence, LazyAttribute, LazyFunction
from factory.django import DjangoModelFactory
from sme_ptrf_apps.core.models.recurso import Recurso

fake = Faker("pt_BR")


class TipoAcertoDocumentoFactory(DjangoModelFactory):
    class Meta:
        model = TipoAcertoDocumento

    nome = Sequence(lambda n: f"Tipo Acerto {n}")
    categoria = LazyAttribute(lambda x: fake.random_element(
        elements=[choice[0] for choice in TipoAcertoDocumento.CATEGORIA_CHOICES]))
    recurso = LazyFunction(lambda: Recurso.objects.get(legado=True))