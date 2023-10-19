from factory import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta

fake = Faker("pt_BR")

class PrestacaoContaFactory(DjangoModelFactory):
    class Meta:
        model = PrestacaoConta
