from factory import DjangoModelFactory, SubFactory, Sequence, LazyAttribute
from faker import Faker
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.core.fixtures.factories.unidade_factory import UnidadeFactory

fake = Faker("pt_BR")

class AssociacaoFactory(DjangoModelFactory):
    class Meta:
        model = Associacao

    unidade = SubFactory(UnidadeFactory)
    cnpj = Sequence(lambda n: fake.unique.cnpj())
    
    
    @LazyAttribute
    def nome(self):
        return f"APM {self.unidade.nome}"
    
