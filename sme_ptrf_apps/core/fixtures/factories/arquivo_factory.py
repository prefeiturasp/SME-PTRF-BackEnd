from factory import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.models.arquivo import Arquivo

fake = Faker("pt_BR")

class ArquivoFactory(DjangoModelFactory):
    class Meta:
        model = Arquivo

    # TODO adicionar outros campos
