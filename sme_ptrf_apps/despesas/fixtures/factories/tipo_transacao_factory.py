from factory import DjangoModelFactory, SubFactory
from faker import Faker
from sme_ptrf_apps.despesas.models.tipo_transacao import TipoTransacao

fake = Faker("pt_BR")

class TipoTransacaoFactory(DjangoModelFactory):
    class Meta:
        model = TipoTransacao

    nome = fake.currency_code()
