from factory import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.models.acao import Acao

fake = Faker("pt_BR")

class AcaoFactory(DjangoModelFactory):
    class Meta:
        model = Acao

    # TODO adicionar outros campos
