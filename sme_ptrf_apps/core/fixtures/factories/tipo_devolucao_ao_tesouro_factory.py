from factory import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.models.tipo_devolucao_ao_tesouro import TipoDevolucaoAoTesouro

fake = Faker("pt_BR")

class TipoDevolucaoAoTesouroFactory(DjangoModelFactory):
    class Meta:
        model = TipoDevolucaoAoTesouro

