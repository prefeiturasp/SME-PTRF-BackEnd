from factory import DjangoModelFactory, SubFactory, Sequence
from faker import Faker
from sme_ptrf_apps.core.models.proccessos_associacao import ProcessoAssociacao
from .associacao_factory import AssociacaoFactory

fake = Faker("pt_BR")

class ProcessoAssociacaoFactory(DjangoModelFactory):
    class Meta:
        model = ProcessoAssociacao

    associacao = SubFactory(AssociacaoFactory)
    numero_processo = Sequence(lambda n: f"{str(fake.unique.random_int(min=10000, max=99999))}")
    ano = Sequence(lambda n: fake.date(pattern="%Y"))
