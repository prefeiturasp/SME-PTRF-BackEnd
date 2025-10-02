from factory.django import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.models.analise_conta_prestacao_conta import AnaliseContaPrestacaoConta
fake = Faker("pt_BR")


class AnaliseContaPrestacaoContaFactory(DjangoModelFactory):
    class Meta:
        model = AnaliseContaPrestacaoConta
