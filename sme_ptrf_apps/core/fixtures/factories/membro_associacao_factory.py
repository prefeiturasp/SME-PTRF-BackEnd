from factory import DjangoModelFactory
from faker import Faker
from sme_ptrf_apps.core.models.membro_associacao import MembroAssociacao

fake = Faker("pt_BR")

class MembroAssociacaoFactory(DjangoModelFactory):
    class Meta:
        model = MembroAssociacao

