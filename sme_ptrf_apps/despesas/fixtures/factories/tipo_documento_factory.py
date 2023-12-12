from factory import DjangoModelFactory, SubFactory
from faker import Faker
from sme_ptrf_apps.despesas.models.tipo_documento import TipoDocumento

fake = Faker("pt_BR")

class TipoDocumentoFactory(DjangoModelFactory):
    class Meta:
        model = TipoDocumento
