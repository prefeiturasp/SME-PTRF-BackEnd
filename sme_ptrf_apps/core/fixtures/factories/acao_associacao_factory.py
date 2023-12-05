from factory import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.models.acao_associacao import AcaoAssociacao

fake = Faker("pt_BR")

class AcaoAssociacaoFactory(DjangoModelFactory):
    class Meta:
        model = AcaoAssociacao

    # TODO adicionar outros campos
