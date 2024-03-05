from factory import DjangoModelFactory, Sequence, LazyAttribute
from faker import Faker
from sme_ptrf_apps.core.models.tipo_acerto_lancamento import TipoAcertoLancamento

fake = Faker("pt_BR")


class TipoAcertoLancamentoFactory(DjangoModelFactory):
    class Meta:
        model = TipoAcertoLancamento

    nome = Sequence(lambda n: fake.unique.word())
    categoria = LazyAttribute(lambda x: fake.random_element(
        elements=[choice[0] for choice in TipoAcertoLancamento.CATEGORIA_CHOICES]))
