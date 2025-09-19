from factory import Sequence
from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.models.tipo_documento_prestacao_conta import TipoDocumentoPrestacaoConta

fake = Faker("pt_BR")


class TipoDocumentoPrestacaoContaFactory(DjangoModelFactory):
    class Meta:
        model = TipoDocumentoPrestacaoConta

    nome = Sequence(lambda n: f"{fake.word()}_{n:06d}")
    documento_por_conta = False
    e_relacao_bens = False
