from factory import DjangoModelFactory, SubFactory, Sequence, LazyAttribute
from faker import Faker
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.core.fixtures.factories.periodo_factory import PeriodoFactory, PeriodoFactoryComDataFixa
from sme_ptrf_apps.core.fixtures.factories.unidade_factory import UnidadeFactory


fake = Faker("pt_BR")

class AssociacaoFactory(DjangoModelFactory):
    class Meta:
        model = Associacao

    unidade = SubFactory(UnidadeFactory)
    cnpj = Sequence(lambda n: fake.unique.cnpj())
    nome =  Sequence(lambda n: fake.unique.name())
    ccm = Sequence(lambda n: 'CCM{:03d}'.format(n)[:15])

    @LazyAttribute
    def nome(self):
        return f"APM {self.unidade.nome}"


class AssociacaoFactoryComPeriodoInicial(AssociacaoFactory):
    periodo_inicial = SubFactory(PeriodoFactoryComDataFixa)
